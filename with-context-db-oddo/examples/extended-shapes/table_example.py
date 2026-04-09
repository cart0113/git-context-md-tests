"""
Example demonstrating table shapes: Table, EntityTable, and KeyValueTable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli
from od_do.diagram import Diagram
from od_do.shapes import table
from od_do import colors


class TableExampleDiagram(Diagram):
    def draw(self):
        # Section 1: Basic Table with header
        table.Table(
            parent=self,
            ll=(50, 200),
            columns=["Name", "Type", "Description"],
            rows=[
                ["id", "int", "Primary key"],
                ["name", "string", "User name"],
                ["email", "string", "Email address"],
                ["created_at", "datetime", "Creation timestamp"],
            ],
            header_fill=colors.DARK_BLUE,
            header_text_color=colors.WHITE,
            fill=colors.WHITE,
            stroke=colors.BLACK,
            font_size=11,
        )

        # Section 2: Table with alternating row colors
        table.Table(
            parent=self,
            ll=(350, 200),
            columns=["Product", "Price", "Stock"],
            rows=[
                ["Widget A", "$19.99", "150"],
                ["Widget B", "$24.99", "75"],
                ["Gadget X", "$49.99", "30"],
                ["Gadget Y", "$89.99", "12"],
            ],
            header_fill=colors.DARK_GREEN,
            header_text_color=colors.WHITE,
            fill=colors.WHITE,
            stroke=colors.DARK_GRAY,
            alternate_fill=colors.LIGHT_GRAY,
            font_size=11,
        )

        # Section 3: EntityTable for ER diagrams
        table.EntityTable(
            parent=self,
            ll=(50, 380),
            title="users",
            rows=[
                ("id", "INT", "PK"),
                ("username", "VARCHAR(50)", "UK"),
                ("email", "VARCHAR(255)", "UK"),
                ("password_hash", "VARCHAR(128)", ""),
                ("created_at", "TIMESTAMP", ""),
            ],
            title_fill=colors.DARK_BLUE,
            title_text_color=colors.WHITE,
            fill=colors.WHITE,
            stroke=colors.DARK_BLUE,
        )

        table.EntityTable(
            parent=self,
            ll=(250, 380),
            title="orders",
            rows=[
                ("id", "INT", "PK"),
                ("user_id", "INT", "FK"),
                ("total", "DECIMAL(10,2)", ""),
                ("status", "VARCHAR(20)", ""),
                ("created_at", "TIMESTAMP", ""),
            ],
            title_fill=colors.DARK_GREEN,
            title_text_color=colors.WHITE,
            fill=colors.WHITE,
            stroke=colors.DARK_GREEN,
        )

        table.EntityTable(
            parent=self,
            ll=(450, 380),
            title="order_items",
            rows=[
                ("id", "INT", "PK"),
                ("order_id", "INT", "FK"),
                ("product_id", "INT", "FK"),
                ("quantity", "INT", ""),
                ("price", "DECIMAL(10,2)", ""),
            ],
            title_fill=colors.PURPLE,
            title_text_color=colors.WHITE,
            fill=colors.WHITE,
            stroke=colors.PURPLE,
        )

        # Section 4: KeyValueTable for configuration/properties
        table.KeyValueTable(
            parent=self,
            ll=(50, 520),
            items=[
                ("Host", "localhost"),
                ("Port", "5432"),
                ("Database", "myapp_prod"),
                ("SSL", "enabled"),
            ],
            key_fill=colors.LIGHT_GRAY,
            fill=colors.WHITE,
            stroke=colors.DARK_GRAY,
            font_size=11,
        )

        table.KeyValueTable(
            parent=self,
            ll=(220, 520),
            items=[
                ("Version", "2.1.0"),
                ("Build", "1847"),
                ("Environment", "production"),
                ("Region", "us-west-2"),
            ],
            key_fill=colors.LIGHT_BLUE,
            key_text_color=colors.DARK_BLUE,
            fill=colors.WHITE,
            stroke=colors.DARK_BLUE,
            font_size=11,
        )

        # Section 5: Custom styled table
        table.Table(
            parent=self,
            ll=(400, 520),
            columns=["Status", "Count"],
            rows=[
                ["Active", "1,245"],
                ["Pending", "89"],
                ["Failed", "12"],
            ],
            header_fill=colors.GOLD,
            header_text_color=colors.BLACK,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            font_size=12,
            row_height=28,
            header_height=32,
        )


if __name__ == "__main__":
    cli()
