class PassagePointer:
    BEFORE_START = 0
    IN_PASSAGE = 1
    AFTER_END = 2

    def __init__(self, start_verse, end_verse):
        self.start_verse = start_verse
        self.current_verse = start_verse
        self.end_verse = end_verse
        self.last_section = None
        self.state = PassagePointer.BEFORE_START
    
    def update_last_section(self, section):
        self.last_section = section
    
    def update_state(self, verse_text):
        self.set_current_verse(verse_text)
        if self.current_verse >= self.start_verse:
            self.state = PassagePointer.IN_PASSAGE
        if self.end_verse != -1 and self.current_verse > self.end_verse:
            self.state = PassagePointer.AFTER_END

    def set_current_verse(self, verse_text):
        self.current_verse = int(verse_text)

    def __str__(self):
        return str(self.current_verse)