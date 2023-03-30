def build_global_declaration(declarations: str) -> str:
    template = ""
    template += f'<declaration>// Place global declarations here.\n'
    template += declarations
    template += f'</declaration>\n'
    return template
