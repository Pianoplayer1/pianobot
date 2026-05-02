"""Interactive paginated message view plus send_table helpers."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from discord import ButtonStyle, Interaction, Message, WebhookMessage, ui

from utils import paginate

log = logging.getLogger(__name__)


class PaginatorView(ui.View):
    """Message view with prev/next buttons and an optional asc/desc flip."""

    def __init__(self, pages_desc: list[str], pages_asc: list[str] | None) -> None:
        """Seed the view with pre-rendered descending pages (+ optional ascending)."""
        super().__init__(timeout=300)
        self.page = 0
        self.pages_desc = pages_desc
        self.pages_asc = pages_asc
        self.current = pages_desc
        self.message: Message | WebhookMessage | None = None
        if pages_asc is None:
            self.remove_item(self.flip)
        self._update_buttons()

    def _update_buttons(self) -> None:
        last = len(self.current) - 1
        self.first.disabled = self.page == 0
        self.prev.disabled = self.page == 0
        self.next.disabled = self.page == last
        self.last.disabled = self.page == last

    async def _show_page(self, interaction: Interaction) -> None:
        self._update_buttons()
        await interaction.response.edit_message(
            content=self.current[self.page],
            view=self,
        )

    async def on_timeout(self) -> None:
        """Strip the buttons off the rendered message once the view expires."""
        if self.message is not None:
            try:
                content = self.current[self.page]
                await self.message.edit(content=content, view=None)
            except Exception as exc:
                log.debug("on_timeout edit failed: %s", exc)

    @ui.button(emoji="⏮", style=ButtonStyle.gray)
    async def first(
        self, interaction: Interaction, _: ui.Button[PaginatorView]
    ) -> None:
        """Jump to the first page."""
        self.page = 0
        await self._show_page(interaction)

    @ui.button(emoji="◀", style=ButtonStyle.gray)
    async def prev(self, interaction: Interaction, _: ui.Button[PaginatorView]) -> None:
        """Go one page back."""
        self.page = max(0, self.page - 1)
        await self._show_page(interaction)

    @ui.button(emoji="🔁", style=ButtonStyle.gray)
    async def flip(self, interaction: Interaction, _: ui.Button[PaginatorView]) -> None:
        """Swap between ascending and descending sort orders."""
        if self.pages_asc is None:
            await interaction.response.defer()
            return
        self.current = (
            self.pages_asc if self.current is self.pages_desc else self.pages_desc
        )
        self.page = 0
        await self._show_page(interaction)

    @ui.button(emoji="▶", style=ButtonStyle.gray)
    async def next(self, interaction: Interaction, _: ui.Button[PaginatorView]) -> None:
        """Advance one page."""
        self.page = min(len(self.current) - 1, self.page + 1)
        await self._show_page(interaction)

    @ui.button(emoji="⏭", style=ButtonStyle.gray)
    async def last(self, interaction: Interaction, _: ui.Button[PaginatorView]) -> None:
        """Jump to the last page."""
        self.page = len(self.current) - 1
        await self._show_page(interaction)


async def send_table(
    send: Callable[..., Awaitable[Message]],
    columns: dict[str, int],
    rows: list[list[str]],
    *,
    flippable: bool = True,
    page_size: int = 15,
    separator_rows: int = 5,
    enum: bool = True,
    label_desc: str | None = "(Descending Order)",
    label_asc: str | None = "(Ascending Order)",
    leading_text: str | None = None,
) -> Message:
    """Render `rows` as a paginated table and send it via the given `send` callable."""
    cols = list(columns.items())
    pages_desc = paginate(
        cols,
        rows,
        page_size=page_size,
        enum=enum,
        separator_rows=separator_rows,
        label=label_desc if flippable else None,
        leading_text=leading_text,
    )
    pages_asc = None
    if flippable:
        pages_asc = paginate(
            cols,
            list(reversed(rows)),
            page_size=page_size,
            enum=enum,
            separator_rows=separator_rows,
            label=label_asc,
            leading_text=leading_text,
        )

    view: PaginatorView | None = None
    if len(pages_desc) > 1 or pages_asc is not None:
        view = PaginatorView(pages_desc, pages_asc)

    if view:
        message: Message = await send(content=pages_desc[0], view=view)
    else:
        message = await send(content=pages_desc[0])
    if view is not None:
        view.message = message
    return message


async def send_table_response(
    interaction: Interaction,
    columns: dict[str, int],
    rows: list[list[str]],
    *,
    flippable: bool = True,
    page_size: int = 15,
    separator_rows: int = 5,
    enum: bool = True,
    leading_text: str | None = None,
) -> None:
    """Send a paginated table as a reply to a slash-command `Interaction`."""
    cols = list(columns.items())
    pages_desc = paginate(
        cols,
        rows,
        page_size=page_size,
        enum=enum,
        separator_rows=separator_rows,
        label="(Descending Order)" if flippable else None,
        leading_text=leading_text,
    )
    pages_asc = None
    if flippable:
        pages_asc = paginate(
            cols,
            list(reversed(rows)),
            page_size=page_size,
            enum=enum,
            separator_rows=separator_rows,
            label="(Ascending Order)",
            leading_text=leading_text,
        )

    view: PaginatorView | None = None
    if len(pages_desc) > 1 or pages_asc is not None:
        view = PaginatorView(pages_desc, pages_asc)

    message: Message | WebhookMessage
    if interaction.response.is_done():
        if view is not None:
            message = await interaction.followup.send(
                content=pages_desc[0], view=view, wait=True
            )
        else:
            message = await interaction.followup.send(content=pages_desc[0], wait=True)
    else:
        if view is not None:
            await interaction.response.send_message(content=pages_desc[0], view=view)
        else:
            await interaction.response.send_message(content=pages_desc[0])
        message = await interaction.original_response()
    if view is not None:
        view.message = message
