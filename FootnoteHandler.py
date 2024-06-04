class FootnoteHandler:
    def __init__(self):
        self.text_notes = []
        self.next_note_label = "a"
        pass
    
    def add_note(self, footnote_section):
        footnote = footnote_section.getText()[1:] # Need to extract italics etc in future
        label = self.next_note_label
        self.text_notes.append( (label, footnote) )
        self.update_next_note_label()
        return label
    
    def update_next_note_label(self):
        self.next_note_label = chr(ord(self.next_note_label)+1)
    
    def print_notes(self):
        out = "\n".join([f"{label}: {note}" for label, note in self.text_notes])
        return out