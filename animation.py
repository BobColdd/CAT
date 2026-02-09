from manim import *

class ExcelLookupTutorial(Scene):
    def construct(self):
        # ===== SCENE 1: TITLE =====
        title = Text("Excel Lookup Functions", font_size=48, color=BLUE)
        subtitle = Text("VLOOKUP vs XLOOKUP", font_size=32, color=YELLOW)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # ===== SCENE 2: THE PROBLEM =====
        problem_title = Text("The Problem: Separate Data Tables", font_size=36)
        problem_title.to_edge(UP)
        
        # Create two tables
        products_table = self.create_table(
            headers=["Product ID", "Product Name", "Price"],
            data=[
                ["P-100", "Laptop", "$999"],
                ["P-101", "Mouse", "$25"],
                ["P-102", "Keyboard", "$89"],
                ["P-103", "Monitor", "$350"]
            ],
            position=LEFT * 3,
            title="Products Table"
        )
        
        sales_table = self.create_table(
            headers=["Sale ID", "Product ID", "Quantity"],
            data=[
                ["S-001", "P-101", "15"],
                ["S-002", "P-103", "3"],
                ["S-003", "P-100", "7"],
                ["S-004", "P-102", "22"]
            ],
            position=RIGHT * 3,
            title="Sales Table"
        )
        
        question = Text("How to get Product Name in Sales Table?", font_size=28, color=RED)
        question.next_to(products_table, DOWN, buff=1)
        
        self.play(Write(problem_title))
        self.play(Create(products_table), Create(sales_table))
        self.wait(1)
        self.play(Write(question))
        self.wait(2)
        
        # ===== SCENE 3: VLOOKUP EXPLANATION =====
        self.play(
            FadeOut(problem_title),
            question.animate.become(Text("Solution 1: VLOOKUP", font_size=36, color=GREEN))
        )
        
        # Highlight Product ID column
        product_id_cells = products_table.get_columns()[0][1:]  # Skip header
        highlight_box = SurroundingRectangle(
            VGroup(*product_id_cells),
            color=YELLOW,
            buff=0.1,
            stroke_width=3
        )
        
        self.play(Create(highlight_box))
        vlookup_formula = Text(
            '=VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])',
            font_size=20,
            font="Monospace"
        )
        vlookup_formula.next_to(question, DOWN, buff=0.5)
        
        self.play(Write(vlookup_formula))
        self.wait(1)
        
        # Animate the lookup process
        lookup_example = Text('=VLOOKUP("P-101", A2:C5, 2, FALSE)', 
                            font_size=24, font="Monospace", color=YELLOW)
        lookup_example.next_to(vlookup_formula, DOWN, buff=0.5)
        
        self.play(Write(lookup_example))
        
        # Create visual connection
        start_point = sales_table.get_cell((2, 2)).get_center()  # First Product ID in sales
        end_point = products_table.get_cell((2, 1)).get_center()  # Matching Product ID
        arrow = Arrow(start_point, end_point, color=GREEN, buff=0.1)
        
        result_cell = Rectangle(
            height=0.5, width=1.5,
            color=BLUE,
            fill_opacity=0.3,
            stroke_width=2
        )
        result_cell.move_to(sales_table.get_columns()[3][1].get_center())
        result_text = Text("Mouse", font_size=20, color=WHITE).move_to(result_cell.get_center())
        
        self.play(Create(arrow))
        self.wait(0.5)
        self.play(
            FadeIn(result_cell),
            Write(result_text)
        )
        self.wait(2)
        
        # ===== SCENE 4: VLOOKUP LIMITATIONS =====
        limitations_title = Text("VLOOKUP Limitations", font_size=32, color=RED)
        limitations_title.to_edge(UP)
        
        limitations = BulletedList(
            "Looks right only",
            "Slow on large datasets",
            "Column index breaks if columns move",
            "Cannot look left",
            font_size=24
        )
        limitations.next_to(limitations_title, DOWN, buff=0.5)
        
        self.play(
            FadeOut(arrow, result_cell, result_text, lookup_example, highlight_box),
            Transform(question, limitations_title),
            FadeIn(limitations)
        )
        self.wait(3)
        
        # ===== SCENE 5: XLOOKUP SOLUTION =====
        self.play(
            FadeOut(limitations),
            question.animate.become(Text("Solution 2: XLOOKUP (Excel 365+)", 
                                        font_size=36, color=GREEN))
        )
        
        xlookup_formula = Text(
            '=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])',
            font_size=18,
            font="Monospace"
        )
        xlookup_formula.next_to(question, DOWN, buff=0.5)
        
        self.play(Write(xlookup_formula))
        self.wait(1)
        
        xlookup_example = Text('=XLOOKUP(B2, Products!A:A, Products!B:B, "Not Found")',
                              font_size=24, font="Monospace", color=YELLOW)
        xlookup_example.next_to(xlookup_formula, DOWN, buff=0.5)
        
        self.play(Write(xlookup_example))
        
        # Animate bidirectional lookup
        left_arrow = Arrow(
            start_point,
            products_table.get_cell((2, 2)).get_center(),
            color=BLUE,
            buff=0.1
        )
        right_arrow = Arrow(
            sales_table.get_cell((3, 2)).get_center(),
            products_table.get_cell((4, 2)).get_center(),
            color=BLUE,
            buff=0.1
        )
        
        self.play(Create(left_arrow), Create(right_arrow))
        self.wait(2)
        
        # ===== SCENE 6: COMPARISON TABLE =====
        self.play(
            FadeOut(products_table, sales_table, left_arrow, right_arrow, 
                   xlookup_formula, xlookup_example),
            question.animate.become(Text("Comparison: VLOOKUP vs XLOOKUP", 
                                        font_size=36, color=WHITE))
        )
        
        comparison_table = Table(
            [
                ["Feature", "VLOOKUP", "XLOOKUP"],
                ["Lookup direction", "Right only", "Any direction"],
                ["Default match", "Approximate", "Exact"],
                ["Search mode", "Top to bottom", "Multiple options"],
                ["If not found", "#N/A error", "Custom message"],
                ["Columns move", "Breaks", "Still works"],
                ["Ease of use", "Harder", "Easier"]
            ],
            include_outer_lines=True,
            line_config={"stroke_width": 1}
        )
        
        # Style the table
        comparison_table.scale(0.5)
        comparison_table.move_to(ORIGIN)
        
        # Color headers
        comparison_table.add_highlighted_cell((1, 1), color=BLUE)
        comparison_table.add_highlighted_cell((1, 2), color=RED)
        comparison_table.add_highlighted_cell((1, 3), color=GREEN)
        
        self.play(Create(comparison_table))
        self.wait(2)
        
        # ===== SCENE 7: FINAL RECOMMENDATION =====
        self.play(FadeOut(comparison_table))
        
        recommendation = Text("Recommendation:", font_size=36, color=YELLOW)
        recommendation.shift(UP * 2)
        
        xlookup_rec = Text("Use XLOOKUP if you have Excel 365+", 
                          font_size=32, color=GREEN)
        vlookup_rec = Text("Use VLOOKUP for compatibility with older Excel", 
                          font_size=28, color=YELLOW)
        
        xlookup_rec.next_to(recommendation, DOWN, buff=0.5)
        vlookup_rec.next_to(xlookup_rec, DOWN, buff=0.5)
        
        final_tip = Text("Tip: Always use FALSE for exact matches in VLOOKUP!",
                        font_size=24, color=BLUE)
        final_tip.next_to(vlookup_rec, DOWN, buff=1)
        
        self.play(Write(recommendation))
        self.play(Write(xlookup_rec))
        self.wait(0.5)
        self.play(Write(vlookup_rec))
        self.wait(0.5)
        self.play(Write(final_tip))
        self.wait(3)
    
    def create_table(self, headers, data, position, title=""):
        """Helper function to create a styled table"""
        # Combine headers and data
        all_data = [headers] + data
        
        # Create table
        table = Table(
            all_data,
            include_outer_lines=True,
            line_config={"stroke_width": 2}
        )
        
        # Style the table
        table.scale(0.4)
        table.move_to(position)
        
        # Highlight header row
        header_cells = table.get_rows()[0]
        for cell in header_cells:
            cell.set_fill(BLUE, opacity=0.3)
            cell.set_color(WHITE)
        
        # Add title if provided
        if title:
            title_text = Text(title, font_size=20, color=YELLOW)
            title_text.next_to(table, UP, buff=0.3)
            table.add(title_text)
        
        return table


# ===== SIMPLER VERSION FOR QUICK TESTING =====
class QuickLookupDemo(Scene):
    """Simpler version for testing"""
    def construct(self):
        # Create two simple tables
        main_table = Table(
            [
                ["ID", "Name", "Price"],
                ["P100", "Laptop", "$999"],
                ["P101", "Mouse", "$25"],
                ["P102", "Keyboard", "$89"]
            ],
            include_outer_lines=True
        ).scale(0.5).shift(LEFT * 3)
        
        lookup_table = Table(
            [
                ["Sale", "Product ID"],
                ["S01", "P101"],
                ["S02", "P100"],
                ["S03", "P102"]
            ],
            include_outer_lines=True
        ).scale(0.5).shift(RIGHT * 3)
        
        # Show tables
        self.play(Create(main_table), Create(lookup_table))
        self.wait(1)
        
        # Show VLOOKUP formula
        formula = Text('=VLOOKUP("P101", A2:C4, 2, FALSE)', 
                      font_size=24, font="Monospace", color=YELLOW)
        formula.shift(DOWN * 2)
        
        self.play(Write(formula))
        self.wait(2)
        
        # Draw connection arrow
        arrow = Arrow(
            lookup_table.get_cell((2, 2)).get_center(),
            main_table.get_cell((2, 2)).get_center(),
            color=GREEN,
            buff=0.1
        )
        
        self.play(Create(arrow))
        self.wait(2)