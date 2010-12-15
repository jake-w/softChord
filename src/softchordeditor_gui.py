# -*- coding: utf-8 -*-
"""

The main source file for softChord Editor

Writen by: Matvey Adzhigirey
Development started in December 2010

"""

# NOTE The sqlite3 is intentionally used instead of QtSql.

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt
import sys, os
import codecs

import sqlite3




#print 'executable:', sys.executable
#print 'dir executable:', dir(sys.executable)
if not os.path.basename(sys.executable).startswith("python"):
    exec_dir = os.path.dirname(sys.executable)
else:
    exec_dir = "."

script_ui_file = os.path.join(exec_dir, "softchordeditor.ui" )
chord_dialog_ui_file = os.path.join(exec_dir, "softchordeditor_chord_dialog.ui")

print 'script_ui_file:', script_ui_file
print 'exists:', os.path.isfile(script_ui_file)


db_file = os.path.join( exec_dir, "song_database.sqlite" )



def tr(text):
    """
    Returns translated GUI text.
    """
    return text




class SongTableModel(QtCore.QAbstractTableModel):
    """
    Class for storing table information.
    """
    def __init__(self, app):
        QtCore.QAbstractTableModel.__init__(self)
        self.app = app
        self._data = []
        self.header_list = ["ID", "Number", "Title"]
        self.updateFromDatabase()

    def updateFromDatabase(self):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._data = []
        for row in self.app.execute("SELECT id, number, title FROM songs"):
            self._data.append(row)
        self.emit(QtCore.SIGNAL("layoutChanged()")) # Forces the view to redraw
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Returns number of rows """
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Returns number of columns """
        return len(self.header_list)
    
    def data(self, index, role=Qt.DisplayRole):
        """
        Given a cell index, returns the data that should be displayed in that
        cell (text or check button state). Used by the view.
        """
        
        if role == Qt.DisplayRole:
            row_data = self._data[index.row()]
            return QtCore.QVariant( row_data[index.column()] )
        return QtCore.QVariant()
    
    def headerData(self, section, orientation, role):
        """
        Returns the string that should be displayed in the specified header
        cell. Used by the View.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.header_list[section])
        return QtCore.QVariant()        
    




class SongChord:
    """
    Class that stores specific chord information. This chord is for a
    specific letter in a specific song.
    """
    
    def __init__(self, app, id, song_id, character_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses):
        self.app = app
        self.id = id
        self.song_id = song_id
        self.character_num = character_num
        self.note_id = note_id
        self.chord_type_id = chord_type_id
        self.bass_note_id = bass_note_id
        if marker == u"-1":
            self.marker = None
        self.marker = marker
        self.in_parentheses = in_parentheses


    def transpose(self, steps):
        """
        Transpose this chord the specified number of steps up.
        <steps> can be negative.
        """
        self.note_id += steps
        if self.note_id < 0:
            self.note_id += 12
        elif self.note_id > 11:
            self.note_id -= 12
        
        if self.bass_note_id != -1:
            self.bass_note_id += steps
            if self.bass_note_id < 0:
                self.bass_note_id += 12
            elif self.bass_note_id > 11:
                self.bass_note_id -= 12

        self.app.execute("UPDATE song_chord_link SET note_id=%i, bass_note_id=%i WHERE id=%i" % (self.note_id, self.bass_note_id, self.id))
        
    
    def _getNoteString(self, note_id):
        """
        Returns the specified note as a string, using sharps vs flats
        as appropriate.
        """

        for row in self.app.execute("SELECT text, alt_text FROM notes WHERE id=%i" % note_id):
            note_text = row[0]
            note_alt_text = row[1]
            
            if self.app.sharpsOrFlats() == 1:
                return note_text
            else:
                return note_alt_text
        
    def getChordString(self):
        """
        Returns string of the chord.
        For example, "Fm" or "Bbsus4"
        """
        note_text = self._getNoteString(self.note_id)
        
        chord_type_text = ""
        for row in self.app.execute("SELECT print FROM chord_types WHERE id=%i" % self.chord_type_id):
            chord_type_text = row[0]
        
        if self.marker: # Not NULL
            chord_str = '%s:%s%s' % (self.marker, note_text, chord_type_text)
        else:
            chord_str = '%s%s' % (note_text, chord_type_text)
        
        if self.bass_note_id != -1: # Not NULL
            bass_note_text = self._getNoteString(self.bass_note_id)
            chord_str += "/%s" % bass_note_text
        
        if self.in_parentheses:
            chord_str = "(%s)" % chord_str

        return chord_str
    

class Song:
    """
    Stores information for a particular song.
    """
    def __init__(self, app, song_id):
        self.app = app
        self.id = song_id
        
        for row in self.app.execute("SELECT title, number, text, key_note_id, key_is_major FROM songs WHERE id=%i" % song_id):
            self.title = row[0]
            self.number = row[1]
            self.all_text = row[2]
            self.key_note_id = row[3] # Can be None or -1
            if self.key_note_id == None:
                self.key_note_id = -1
            self.key_is_major = row[4]
            break
        
        song_chords = {}
        for row in self.app.execute("SELECT id, character_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses FROM song_chord_link WHERE song_id=%i" % song_id):
            id = row[0]
            song_char_num = row[1]
            note_id = row[2]
            chord_type_id = row[3]
            bass_note_id = row[4]
            marker = row[5]
            in_parentheses = row[6]
            song_chords[song_char_num] = SongChord(app, id, song_id, song_char_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses)
        self.all_chords = song_chords

        
        # Break the song text into multiple lines:
        self._lines_list = []
        line_start_offset = 0
        line_end_offset = None
        

        #for row in app.execute("SELECT id, character_num, note_id, chord_type_id, bass_note_id, marker FROM song_chord_link WHERE song_id=%i" % song_id):
        #    print 'row:', row
        #    #for id, song_char_num

        self.all_text = unicode(self.all_text)
        remaining_text = self.all_text
        
        exit = False
        while not exit:
            char_num = unicode(remaining_text).find('\n')
            if char_num == -1:
                # This is the last line in the song
                exit = True
                line_text = remaining_text # text for this line
                line_end_offset = len(line_text) + line_start_offset
            else:
                # This is NOT the last line in the song
                line_text = remaining_text[:char_num] # text for this line
                remaining_text = remaining_text[char_num+1:]
                line_end_offset = char_num + line_start_offset
            
            self._lines_list.append(line_text)
            
            if char_num:
                # The start of the next line will be offset by char_num:
                line_start_offset += char_num+1
    

    def getNumLines(self):
        """
        Returns the number of lines in this song.
        """
        return len(self._lines_list)
    
    def getLineText(self, linenum):
        """
        Return the text for the specified line.
        """
        return self._lines_list[linenum]
    
    def iterateOverLines(self):
        """
        Iterate over each the lines in this song.
        """
        for line in self._lines_list:
            yield line

    def songCharToLineChar(self, song_char_num):
        """
        Given a character's global position in the song, return the
        character's line and line position.

        Returns a tuple of (linenum, char_num)
        """
        
        line_global_start = 0
        line_global_end = 0
        linenum = -1
        for line_text in self.iterateOverLines():
            linenum += 1
            line_global_end += len(line_text) + 1
            if song_char_num < line_global_end-1:
                # This character is in this line
                line_char_num = song_char_num - line_global_start
                return (linenum, line_char_num)
            line_global_start += len(line_text) + 1
        
        raise RuntimeError()


    def lineCharToSongChar(self, char_linenum, char_num):
        """
        Given the character position in the line, return its global
        position in the song.
        """
        
        out_char_num = 0
        linenum = -1
        for line_text in self.iterateOverLines():
            linenum += 1
            if linenum == char_linenum:
                return out_char_num + char_num
            else:
                out_char_num += len(line_text) + 1 # Add one for the end-of-line character
        raise RuntimeError()


    def getAsText(self):
        """
        Return a text string for this song. This text will have proper
        formatting only if displayed with a mono-spaced (fixed-width) font.
        """
        
        #monospaced_font = QtGui.QFont("Courier", 14)
        #monospaced_metrics = QtGui.QFontMetrics(self.lyrics_font)
        
        song_text = unicode()
        song_text += u"\n" # Song title
        song_text += u"\n" # Blank line
            
        
        for linenum in range(self.getNumLines()):
            line_text = unicode( self.getLineText(linenum) )
            
            line_chord_text_list =  [u' '] * len(line_text) # FIXME add a few to the end???
            
            # Figure out the lyric letter for the mouse location:
            song_char_num = -1
            for line_char_num in range(len(line_text)):
                song_char_num = self.lineCharToSongChar(linenum, line_char_num)
                
                
                # Figure out if a chord is attached to this letter:
                for chord_song_char_num, chord in self.all_chords.iteritems():
                    chord_linenum, line_char_num = self.songCharToLineChar(chord_song_char_num)

                    if chord_linenum != linenum:
                        continue
                        
                    chord_text = chord.getChordString()
                    chord_left = line_char_num - ( len(chord_text) / 2 )
                    chord_right = line_char_num + ( len(chord_text) / 2 )
                    
                    for i in range(len(chord_text)):
                        pos = i + chord_left
                        line_chord_text_list[pos] = chord_text[i]
                    
            line_chord_text = u''.join(line_chord_text_list)

            song_text += u"\n" + line_chord_text
            song_text += u"\n" + line_text
            
        return song_text


class PrintWidget(QtGui.QWidget):
    """
    Widget for painting the current song.
    """
    def __init__(self, app):
        QtGui.QWidget.__init__(self, app.ui)
        self.app = app
        self.dragging_chord_orig_position = -1
        self.dragging_chord_curr_position = -1
        self.copying_chord = False # Whether the chord that is dragged will be copied instead of moved

        # So that hover mouse move events are generated:
        self.setMouseTracking(True)
    
    def paintEvent(self, ignored_event):
        """
        Called when the widget needs to draw the current song.
        """
        
        painter = QtGui.QPainter()
        painter.begin(self)
        
        # Draw into the whole widget:
        rect = self.rect()
        
        bgbrush = QtGui.QBrush(QtGui.QColor("white"))
        painter.fillRect(rect, bgbrush)
        
        if self.app.current_song:
            self.app.drawSongToRect(self.app.current_song, painter, rect)
        
        painter.end()
    

    def leaveEvent(self, event):
        """
        Called when the mouse LEAVES the song chords widget.
        """
        
        # Clear the hovering highlighting:
        self.hover_char_num = None
        self.repaint()

    
    def mouseMoveEvent(self, event):
        """
        Called when mouse is DRAGGED or HOVERED in the song chords widget.
        """
        
        self.app.hover_char_num = None
        
        if self.geometry().contains(event.pos()):
            localx = event.pos().x()
            localy = event.pos().y()
            letter_tuple = self.app.determineClickedLetter(localx, localy)
            if letter_tuple:
                (is_chord, linenum, line_char_num, song_char_num) = letter_tuple
                # Mouse is over a vlid chord/letter
                
                if self.dragging_chord_curr_position == -1:
                    # Hovering, highlight the new chord/letter
                    self.app.hover_char_num = song_char_num

                else:
                    # Dragging
                    if self.dragging_chord_curr_position != -1:
                        # A chord is being dragged
                        
                        if song_char_num != self.dragging_chord_curr_position:
                            # The dragged chord was moved to a new position
                        
                            #key_modifiers = QtGui.QApplication.instance().keyboardModifiers() 
                            key_modifiers = event.modifiers() 
                            # shiftdown = key_modifiers & Qt.ShiftModifier
                            ctrl_down = bool(key_modifiers & Qt.ControlModifier)
                            #print 'ctrl_down:', ctrl_down

                            if self.copying_chord:
                                #print 'currently copying'
                                # The chord is currently drawn in both the original position and the curr_position
                                pass
                                """
                                if not ctrl_down:
                                    #print '  no longer copying, removing orig chord'
                                    # Just stopped copying, remove the orig chord.
                                    self.app.moveChord(self.dragging_chord_orig_position, -1)
                                    self.copying_chord = False
                                """
                            else:
                                #print 'currently not copying'
                                # The chord is currently drawn only in the the curr_position
                                if ctrl_down:
                                    #print '  will start copying, adding the original chord'
                                    # Copy the chord to the original position as well
                                    self.app.moveChord(self.dragging_chord_curr_position, self.dragging_chord_orig_position, copy=True)
                                    self.copying_chord = True
                                #print '  control is not pressed'

                            #print 'moving the dragged chord'
                            self.app.moveChord(self.dragging_chord_curr_position, song_char_num)
                            self.dragging_chord_curr_position = song_char_num
                            
                            # Show hover feedback on the new letter:
                            self.app.hover_char_num = song_char_num
                    else:
                        # No chord is being currently dragged. Clear previous selection:
                        self.app.selected_char_num = song_char_num
        
        self.app.print_widget.repaint()



    def mousePressEvent(self, event):
        """
        Called when mouse is CLICKED in the song chords widget.
        """

        if event.button() == Qt.LeftButton:
            localx = event.pos().x()
            localy = event.pos().y()
            letter_tuple = self.app.determineClickedLetter(localx, localy)
            if letter_tuple:
                # A valid letter/chord was clicked, select it:
                (is_chord, linenum, line_char_num, song_char_num) = letter_tuple
                
                if self.app.selected_char_num == song_char_num and is_chord:
                    # User clicked on the selected chord, initiate drag:
                    self.dragging_chord_curr_position = song_char_num
                    self.dragging_chord_orig_position = song_char_num
                    self.copying_chord = False
                else:
                    # User clicked on an un-selected chord. Select it:
                    self.app.selected_char_num = song_char_num
                    #self.dragging_chord_curr_position = -1
                    #self.dragging_chord_orig_position = -1
                    
                    # Initiate a drag:
                    self.dragging_chord_curr_position = song_char_num
                    self.dragging_chord_orig_position = song_char_num
                    self.copying_chord = False
            else:
                self.app.selected_char_num = None
            self.app.print_widget.repaint()
    

    def mouseReleaseEvent(self, event):
        #if event.button() == Qt.LeftButton:

        # Stop dragging of the chord (it's already in the correct position):
        if self.dragging_chord_curr_position != -1:
            self.dragging_chord_curr_position = -1
            self.dragging_chord_orig_position = -1
        
        
    def mouseDoubleClickEvent(self, event):
        """
        Called when mouse is DOUBLE-CLICKED in the song chords widget.
        """
        
        if event.button() == Qt.LeftButton:
            localx = event.pos().x()
            localy = event.pos().y()
            letter_tuple = self.app.determineClickedLetter(localx, localy)
            if letter_tuple:
                # A valid chord/letter was double-clicked, edit it:
                (is_chord, linenum, line_char_num, song_char_num) = letter_tuple
                self.app.selected_char_num = song_char_num
                self.app.processSongCharEdit(song_char_num)
            else:
                # Invalid chord/letter was double clicked. Clear current selection:
                self.app.selected_char_num = None

            self.app.print_widget.repaint()

    


class ChordDialog:
    """
    Dialog for allowing the user to set the chord note & type.
    """

    def c(self, widget, signal_str, slot):
        self.ui.connect(widget, QtCore.SIGNAL(signal_str), slot)
    def __init__(self, app):
        self.app = app
        self.ui = uic.loadUi(chord_dialog_ui_file)
        
        notes_list = []
        for row in self.app.execute("SELECT id, text, alt_text FROM notes"):
            note_id = row[0]
            text = row[1]
            alt_text = row[2]
            if text == alt_text:
                combined_text = text
            else:
                combined_text = "%s/%s" % (text, alt_text)
            notes_list.append(combined_text)
        self.ui.note_menu.addItems(notes_list)


        chord_types_list = []
        for row in self.app.execute("SELECT id, name FROM chord_types"):
            chord_type_id = row[0]
            name = row[1]
            chord_types_list.append(name)
        self.ui.chord_type_menu.addItems(chord_types_list)

        self.ui.bass_menu.addItems(["None"] + notes_list)
    

    def display(self, chord):
        """
        Display the chord-editing dialog box.
        Returns a modified chord if OK was pressed. Returns None if Cancel.
        """
        
        chord = copy.copy(chord)
        note_id = chord.note_id
        chord_type_id = chord.chord_type_id
        bass_note_id = chord.bass_note_id
        marker = chord.marker
        in_parentheses = chord.in_parentheses
        
        # FIXME add a marker-editing entry field.
        

        if note_id != None:
            self.ui.note_menu.setCurrentIndex(note_id)
        if chord_type_id != None:
            self.ui.chord_type_menu.setCurrentIndex(chord_type_id)
        if bass_note_id != None:
            # -1 becomes 0, etc:
            self.ui.bass_menu.setCurrentIndex(bass_note_id+1)
        
        self.ui.show()
        self.ui.raise_()
        out = self.ui.exec_()
        if out: # OK pressed:
            new_chord = copy.copy(chord)
            new_chord.note_id = self.ui.note_menu.currentIndex()
            new_chord.chord_type_id = self.ui.chord_type_menu.currentIndex()
            # 0 (first item) will become -1 (invalid):
            new_chord.bass_note_id = self.ui.bass_menu.currentIndex() - 1
            new_chord.marker = marker # FIXME
            new_chord.in_parentheses = in_parentheses # FIXME
            
            return new_chord
        else:
            # Cancel pressed
            return None


class App:
    """
    The main application class.
    """
    def c(self, widget, signal_str, slot):
        self.ui.connect(widget, QtCore.SIGNAL(signal_str), slot)
    def __init__(self):
        self.ui = uic.loadUi(script_ui_file)

        #self.info('Database: %s; exists: %s' % (db_file, os.path.isfile(db_file)))
        
        # This will be used for Python (sqlite3) operations:
        self.curs = sqlite3.connect(db_file)
        
        # FOR DEMONSTRATION:
        #for row in self.execute("SELECT * FROM songs"):
        #    print row
        
        
        # Make a list of all keys:
        keys_list = ["None"]
        for row in self.execute("SELECT id, text, alt_text FROM notes"):
            note_id = row[0]
            text = row[1]
            alt_text = row[2]
            if text == alt_text:
                combined_text = text
            else:
                combined_text = text + u'/' + alt_text #u"%s/%s" % (text, alt_text)
            keys_list.append(combined_text + u" Major")
            keys_list.append(combined_text + u" Minor")
        
        self.ui.song_key_menu.addItems(keys_list)
        
        
        self.songs_model = SongTableModel(self)
        
        self.ui.songs_view.setModel(self.songs_model)
        self.ui.songs_view.horizontalHeader().setStretchLastSection(True)
        self.ui.songs_view.verticalHeader().hide()
        self.ui.songs_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.songs_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.c( self.ui.songs_view.selectionModel(), "selectionChanged(QItemSelection, QItemSelection)",
            self.songsSelectionChangedCallback )

        self.updateFromDatabase()
        
        self.ignore_song_text_changed = False
        self.previous_song_text = None # Song text before last user's edit operation
        self.c( self.ui.song_text_edit, "textChanged()", self.songTextChanged )
        
        self.c( self.ui.transpose_up_button, "clicked()", self.transposeUp )
        self.c( self.ui.transpose_down_button, "clicked()", self.transposeDown )
        self.c( self.ui.chord_font_button, "clicked()", self.changeChordFont )
        self.c( self.ui.text_font_button, "clicked()", self.changeLyricsFont )
        self.c( self.ui.export_pdf_button, "clicked()", self.exportToPdf )
        self.c( self.ui.import_text_button, "clicked()", self.importFromText )
        self.c( self.ui.export_text_button, "clicked()", self.exportToText )
        #self.c( self.ui.print_button, "clicked()", self.printSelectedSongs )
        self.c( self.ui.new_song_button, "clicked()", self.createNewSong )
        self.c( self.ui.delete_song_button, "clicked()", self.deleteSelectedSong )
        
        self.c( self.ui.song_title_ef, "textEdited(QString)", self.currentSongTitleEdited )
        self.c( self.ui.song_num_ef, "textEdited(QString)", self.currentSongNumberEdited )
        self.c( self.ui.song_key_menu, "currentIndexChanged(int)", self.currentSongKeyChanged )
        
        # Menu actions:
        self.c( self.ui.actionPrint, "triggered()", self.printSelectedSongs )
        self.c( self.ui.actionNewSong, "triggered()", self.createNewSong )
        self.c( self.ui.actionDeleteSongs, "triggered()", self.deleteSelectedSong )
        self.c( self.ui.actionExportPdf, "triggered()", self.exportToPdf )
        self.c( self.ui.actionExportText, "triggered()", self.exportToText )
        self.c( self.ui.actionImportText, "triggered()", self.importFromText )
        self.c( self.ui.actionLyricsFont, "triggered()", self.changeLyricsFont )
        self.c( self.ui.actionChordsFont, "triggered()", self.changeChordFont )
        
        self.print_widget = PrintWidget(self)
        self.ui.chord_scroll_area.setWidgetResizable(False)
        self.ui.chord_scroll_area.setWidget(self.print_widget)
        # Set the background to white (instead of grey):
        self.ui.chord_scroll_area.setBackgroundRole(QtGui.QPalette.Light)

        
        self.current_song = None
        # The letter/chord that is currently selected:
        self.selected_char_num = None
        # The letter/chord that is currently hover (mouse hoveing over it):
        self.hover_char_num = None
        
        self.lyrics_font = QtGui.QFont("Times", 14)
        self.lyrics_font_metrics = QtGui.QFontMetrics(self.lyrics_font)
        self.chord_font = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        self.chord_font_metrics = QtGui.QFontMetrics(self.chord_font)
        self.ui.song_text_edit.setFont(self.lyrics_font)
        
        self._orig_keyPressEvent = self.ui.keyPressEvent
        self.ui.keyPressEvent = self.keyPressEvent

    def __del__(self):
        pass
    

    def execute(self, query):
        out = self.curs.execute(query)
        self.curs.commit()
        return out
    
    
    def updateFromDatabase(self):
        """
        Re-create the songs model to re-read it from the database.
        """
        
        selected_row_indecies = self.ui.songs_view.selectionModel().selectedRows()
        
        self.songs_model.updateFromDatabase()

        for index in selected_row_indecies:
            self.ui.songs_view.selectRow(index.row())


    def keyPressEvent(self, event):
        """
        Will get called when a key is pressed
        """
        key = event.key()
        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            self.deleteSelectedChord()
        else:
            self._orig_keyPressEvent(event)
    

    def deleteSelectedChord(self):
        """
        Deletes the currently selected chord from the song.
        """
        
        if self.selected_char_num != None and self.current_song:
            song_char_num = self.selected_char_num
            
            song_id = self.current_song.id
            
            self.execute("DELETE FROM song_chord_link WHERE song_id=%i AND character_num=%i" % (song_id, song_char_num))
            
            self.selected_char_num = None
            self.updateCurrentSongFromDatabase()
            self.print_widget.repaint()

    def warning(self, text):
        QtGui.QMessageBox.warning(self.ui, "Warning", text)

    def info(self, text):
        QtGui.QMessageBox.information(self.ui, "Information", text)
    
    def error(self, text):
        QtGui.QMessageBox.warning(self.ui, "Error", text)

    def setWaitCursor(self):
        self.ui.setCursor( QtGui.QCursor(QtCore.Qt.WaitCursor) )

    def restoreCursor(self):
        self.ui.setCursor( QtGui.QCursor(QtCore.Qt.ArrowCursor) )


    def songsSelectionChangedCallback(self, selected=None, deselected=None):
        """
        Called when the song selection changes.
        """
        self.selected_char_num = None # Remove the selection
        self.hover_char_num = None # Remove the hover highlighting
        self.updateCurrentSongFromDatabase()
    

    def getSelectedSongIds(self):
        """
        Returns a list of selected songs (their song_ids)
        """

        selected_song_ids = []
        for index in self.ui.songs_view.selectionModel().selectedRows():
            song_id = self.songs_model.data(index).toInt()[0]
            selected_song_ids.append(song_id)
        return selected_song_ids
    

    def updateCurrentSongFromDatabase(self):
        """
        Re-reads the current song from the database.
        """
        
        selected_song_ids = self.getSelectedSongIds()
        
        if len(selected_song_ids) == 1:
            song_id = selected_song_ids[0]
            self.setCurrentSong(song_id)
            
            # Update the print_widget size:
            widget_width = 0 #self.ui.chord_scroll_area.width() - 20
            widget_height = 0 #self.ui.chord_scroll_area.height() - 2
            line_left = 20

            for linenum, line_text in enumerate(self.current_song.iterateOverLines()):
                chords_top, chords_bottom, lyrics_top, lyrics_bottom = self.getLineHeights(linenum)
                line_right = line_left + self.lyrics_font_metrics.width(line_text)
                if line_right > widget_width:
                    widget_width = line_right
                if lyrics_bottom > widget_height:
                    widget_height = lyrics_bottom
            
            self.print_widget.resize(widget_width, widget_height)
        else:
            self.current_song = None
        
        if self.current_song == None:
            self.ui.song_text_edit.setPlainText("")
            self.previous_song_text = None
            self.ui.song_title_ef.setText("")
            self.ui.song_num_ef.setText("")
            self.ui.song_key_menu.setCurrentIndex(0) # None
        
        self.ui.song_text_edit.setEnabled( self.current_song != None )
        self.ui.song_title_ef.setEnabled( self.current_song != None )
        self.ui.song_num_ef.setEnabled( self.current_song != None )
        self.ui.song_key_menu.setEnabled( self.current_song != None )
        self.ui.delete_song_button.setEnabled( len(selected_song_ids) > 0 )
        
        self.ui.export_pdf_button.setEnabled( len(selected_song_ids) > 0 )
        self.ui.export_text_button.setEnabled( len(selected_song_ids) == 1 )
        
        self.print_widget.repaint()
            
    
    def setCurrentSong(self, song_id):
        """
        Sets the current song to the specified song.
        Reads all song info from the database.
        """
        
        self.current_song = Song(self, song_id)
        
        if not self.ignore_song_text_changed:
            self.ignore_song_text_changed = True
            self.ui.song_text_edit.setPlainText(self.current_song.all_text)
            self.ignore_song_text_changed = False
            self.previous_song_text = self.current_song.all_text
        
        if self.current_song.key_note_id == -1:
            self.ui.song_key_menu.setCurrentIndex( 0 )
        else:
            self.ui.song_key_menu.setCurrentIndex( self.current_song.key_note_id*2 + self.current_song.key_is_major + 1)

        self.ui.song_title_ef.setText(self.current_song.title)
        if self.current_song.number == -1:
            self.ui.song_num_ef.setText("")
        else:
            self.ui.song_num_ef.setText( str(self.current_song.number) )
        


    def sharpsOrFlats(self):
        """
        Returns 0 if "flat" versions of the chord should be printed,
        and returns 1 if "sharp" versions of the chords should be printed
        """
        if not self.current_song:
            return 1
        
        num_prefer_sharp = 0
        num_prefer_flat = 0
        for row in self.execute("SELECT note_id FROM song_chord_link WHERE song_id=%i" % self.current_song.id):
            note_id = row[0]
            if note_id in [1, 6]: # C# or F#
                num_prefer_sharp += 1
            elif note_id in [3, 10]: # Eb or Bb
                num_prefer_flat += 1

        if num_prefer_flat > num_prefer_sharp:
            return 0 # flat
        else:
            return 1 # sharp


    #def songChordLinkDataChanged(self, topLeft, bottomRight):
    #    self.updateCurrentSongFromDatabase()

    def _transposeCurrentSong(self, steps):
        """
        Transpose the current song up by the specified number of steps.
        """
        
        for character_num, chord in self.current_song.all_chords.iteritems():
            chord.transpose(steps)
        self.updateCurrentSongFromDatabase()
    
    def songTextChanged(self):
        """
        Called when the song lyric text is modified by the user.
        """
        if self.ignore_song_text_changed:
            return
        if not self.current_song:
            return
        
        self.ignore_song_text_changed = True
        
        song_text = self.ui.song_text_edit.toPlainText()
        
        # Compare the new text to the previous text:
        
        if self.previous_song_text and self.previous_song_text != song_text:
            
            # For each character: key: old position, value: new position
            renumber_map = {}
            
            i = -1
            while True:
                i += 1
                try:
                    if song_text[i] != self.previous_song_text[i]:
                        break
                    else:
                        renumber_map[i] = i
                except IndexError:
                    # Reached end-of-line of either string
                    break
            num_preserved_begin_chars = i
            
            i = 0
            while True:
                i -= 1
                try:
                    if song_text[i] != self.previous_song_text[i]:
                        break
                    else:
                        renumber_map[ len(self.previous_song_text)+i ] = len(song_text)+i
                except IndexError:
                    # Reached end-of-line of either string
                    break
            num_preserved_end_chars = i
            


            # Renumber the chords:
            tmp_ids_to_delete = []
            tmp_id_song_char_num_dict = {}
            song_id = self.current_song.id
            for row in self.execute("SELECT id, character_num FROM song_chord_link WHERE song_id=%i" % song_id):
                id = row[0]
                song_char_num = row[1]
                try:
                    new_song_char_num = renumber_map[song_char_num]
                    tmp_id_song_char_num_list = []
                except KeyError:
                    tmp_ids_to_delete.append(id)
                else:
                    tmp_id_song_char_num_dict[id] = new_song_char_num
            
            for id in tmp_ids_to_delete:    
                self.execute("DELETE FROM song_chord_link WHERE id=%i" % id)

            for id, new_song_char_num in tmp_id_song_char_num_dict.iteritems():
                self.execute("UPDATE song_chord_link SET character_num=%i WHERE id=%i" % (new_song_char_num, id))


            # Renumber the selection:
            if self.selected_char_num != None:
                self.selected_char_num = renumber_map.get(self.selected_char_num)
        
        self.previous_song_text = song_text
        
        song_id = self.current_song.id
        
        self.execute('UPDATE songs SET text="%s" WHERE id=%i' % (song_text, song_id))
        
        self.updateCurrentSongFromDatabase()
        
        self.ignore_song_text_changed = False
    

    def moveChord(self, song_char_num, new_song_char_num, copy=False):
        """
        Move the specified chord to a new position.
        If new_song_char_num == -1, then the chord is deleted.
        
        If copy is True, then copy the chord instead of moving it.
        """
        
        # Renumber the chords:
        song_id = self.current_song.id
        row = self.execute("SELECT id, note_id, chord_type_id, bass_note_id FROM song_chord_link WHERE song_id=%i AND character_num=%i" % (song_id, song_char_num)).fetchone()
        id = row[0]
        
        if new_song_char_num == -1:
            # Delete
            self.execute("DELETE FROM song_chord_link WHERE id=%i" % id)
        else:
            if copy:
                #print 'copying'
                # Copy
                note_id = row[1]
                chord_type_id = row[2]
                bass_note_id = row[3]
                
                # Get the next available ID:
                row = self.execute("SELECT MAX(id) from song_chord_link").fetchone()
                new_id = row[0] + 1
                
                self.execute("INSERT INTO song_chord_link (id, song_id, character_num, note_id, chord_type_id, bass_note_id) " + \
                            "VALUES (%i, %i, %i, %i, %i, %i)" % (new_id, song_id, new_song_char_num, note_id, chord_type_id, bass_note_id))
            else:
                #print 'moving'
                # Move
                self.execute("UPDATE song_chord_link SET character_num=%i WHERE id=%i" % (new_song_char_num, id))
        self.updateCurrentSongFromDatabase()
    
    
    def transposeUp(self):
        self._transposeCurrentSong(1)

    def transposeDown(self):
        self._transposeCurrentSong(-1)
    
    def changeChordFont(self):
        """
        Brings up a dialog to let the user modify the chords font.
        """
        new_font, ok = QtGui.QFontDialog.getFont(self.chord_font, self.ui)
        if ok:
            self.chord_font = new_font
            self.chord_font_metrics = QtGui.QFontMetrics(self.chord_font)
            self.print_widget.repaint()

    def changeLyricsFont(self):
        """
        Brings up a dialog to let the user modify the lyrics font.
        """
        new_font, ok = QtGui.QFontDialog.getFont(self.lyrics_font, self.ui)
        if ok:
            self.lyrics_font = new_font
            self.lyrics_font_metrics = QtGui.QFontMetrics(self.lyrics_font)
            self.ui.song_text_edit.setFont(self.lyrics_font)
            self.print_widget.repaint()
        
    
    def actionPrint(self):
        print 'actionPrint'
    

    def printSelectedSongs(self):
        """
        Bring up a print dialog box.
        """
        
        printer = QtGui.QPrinter()
        printer.setFullPage(True)
        printer.setPageSize(QtGui.QPrinter.Letter)
        printer.setOrientation(QtGui.QPrinter.Portrait)
        
        painter = QtGui.QPainter()
        
        print_dialog = QtGui.QPrintDialog(printer, self.ui)
        if print_dialog.exec_() == QtGui.QDialog.Accepted:
            print 'printing'
            num_printed = self._paintToPrinter(printer)
            print 'printed %s songs' % num_printed


    """
        QPrinter printer;
        printer.setOutputFormat(QPrinter::PdfFormat);
        printer.setOutputFileName("/foobar/nonwritable.pdf");
        QPainter painter;
        if (! painter.begin(&printer)) { // failed to open file
        qWarning("failed to open file, is it writable?");
        return 1;
        }
        painter.drawText(10, 10, "Test");
        if (! printer.newPage()) {
        qWarning("failed in flushing page to disk, disk full?");
        return 1;
        }
        painter.drawText(10, 10, "Test 2");
        painter.end();
    """

    
    def _paintToPrinter(self, printer):
        """
        Paint current songs to the specified QPriner instance.
        """
        
        #print 'from page:', printer.fromPage()
        #print 'page order:', printer.pageOrder()
        #print 'print range:', printer.printRange()

        painter = QtGui.QPainter()
        painter.begin(printer) # may fail to open the file
        
        num_printed = 0
        for song_index, song_id in enumerate(self.getSelectedSongIds()):
            #print 'exporting song_id:', song_id
            if song_index != 0:
                printer.newPage()
            
            page_height = printer.height()
            page_width = printer.width()
            
            song = Song(self, song_id)
            self.drawSongToRect(song, painter, None, draw_markers=False)
            num_printed += 1
        
        painter.end()
        return num_printed


    def exportToPdf(self):
        """
        Exports the selected songs to a PDF file.
        """

        outfile = QtGui.QFileDialog.getSaveFileName(self.ui,
                    "Save PDF file as:",
                    ".", # initial dir
                    "PDF format (*.pdf)",
        )
        if outfile: 
            #print 'generating PDF:', outfile
            
            num_exported = 0
            self.setWaitCursor()
            try:
                printer = QtGui.QPrinter()
                printer.setFullPage(True)
                #printer.setPageSize(QtGui.QPrinter.Letter)
                printer.setOrientation(QtGui.QPrinter.Portrait)
                printer.setOutputFileName(outfile)
                printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
                
                num_exported = self._paintToPrinter(printer)
            except:
                self.restoreCursor()
                self.error("Error generating PDF")
                raise
            else:
                if num_exported == 1:
                    num_str = "1 song"
                else:
                    num_str = "%i songs" % num_exported
                self.restoreCursor()
                self.info("Exported %s to PDF: %s" % (num_str, outfile))
    
    
    
    def exportToText(self):
        """
        Exports the selected song (one) to a TEXT file.
        """
        
        outfile = "tmp.txt"
        """
        outfile = QtGui.QFileDialog.getSaveFileName(self.ui,
                    "Save text file as:",
                    ".", # initial dir
                    "Text format (*.txt)",
        )
        """
        if outfile: 
            print 'generating text file:', outfile
            
            fh = codecs.open(outfile, 'w', encoding='utf-8')
            fh = open(outfile, 'w')
            
            for song_index, song_id in enumerate(self.getSelectedSongIds()):
                # NOTE for now there will always be only one song exported.
                print 'exporting song_id:', song_id

                song = Song(self, song_id)
                
                # Encode the unicode string as UTF-8 before writing to file:
                song_text = song.getAsText().encode('utf-8')
                
                fh.write(song_text)
            
            fh.close()
            print 'WRITTEN:', outfile

    
    def currentSongTitleEdited(self, new_title):
        """
        Called when the user modifies the selected song's title.
        """
        if self.current_song:
            self.execute('UPDATE songs SET title="%s" WHERE id=%i' % (new_title, self.current_song.id))
            
            # Update the song table from database:
            self.updateFromDatabase()
        
    
    def currentSongNumberEdited(self, new_num_str):
        """
        Called when the user modifies the selected song's number.
        """
        if self.current_song:
            if new_num_str == "":
                new_num_str = -1 # NULL
            try:
                new_num = int(new_num_str)
            except:
                self.error("Invalid song number")
            else:
                self.execute('UPDATE songs SET number=%i WHERE id=%i' % (new_num, self.current_song.id))
                
                # Update the song table from database:
                self.updateFromDatabase()
        
    
    def currentSongKeyChanged(self, new_key_index):
        """
        Called when the user modifies the selected song's key.
        """
        
        if self.current_song == None:
            return
        
        song_id = self.current_song.id
        
        if new_key_index == 0:
            note_id = -1
            is_major = 1
        else:
            note_id = (new_key_index-1) / 2
            is_major = (new_key_index-1) % 2
        
        if note_id != self.current_song.key_note_id and is_major != self.current_song.key_is_major:
            # Do not run this code if the value of the menu is first initialized
            self.execute('UPDATE songs SET key_note_id=%i, key_is_major=%i WHERE id=%i' % (note_id, is_major, song_id))
            
            # Update the song table from database:
            self.updateFromDatabase()
    

    
    def createNewSong(self):
        """
        Add a new song to the database and the songs table, and select it.
        """
        song_text = ""
        song_number = -1 # NULL
        song_title = ""
        
        row = self.execute("SELECT MAX(id) from songs").fetchone()
        id = row[0] + 1
        
        print 'new id:', id

        out = self.execute("INSERT INTO songs (id, number, text, title) " + \
                        'VALUES (%i, %i, "%s", "%s")' % (id, song_number, song_text, song_title))
        print 'out:', out
        
        # Update the song table from database:
        self.updateFromDatabase()
        
        # Select the newly added song:
        self.ui.songs_view.selectRow( self.songs_model.rowCount()-1 )
        self.updateCurrentSongFromDatabase()
    


    def deleteSelectedSong(self):
        self.setWaitCursor()
        try:
            selected_song_ids = self.getSelectedSongIds()
            for song_id in selected_song_ids:
                self.execute("DELETE FROM songs WHERE id=%i" % song_id)
                
                # Delete all associated chords:   
                self.execute("DELETE FROM song_chord_link WHERE song_id=%i" % song_id)
            
            # Update the song table from database:
            self.updateFromDatabase()
        finally:
            self.restoreCursor()

    
    def drawSongToRect(self, song, painter, rect, draw_markers=True):
        """
        Draws the current song text to the specified rect.

        draw_markers - whether to draw the selection & hover markers
        """
        
        selection_brush = QtGui.QPalette().highlight()
        hover_brush = QtGui.QColor("light grey")
        
        line_left = 20

        for linenum, line_text in enumerate(song.iterateOverLines()):
            
            chords_top, chords_bottom, lyrics_top, lyrics_bottom = self.getLineHeights(linenum)
            
            if draw_markers:
                if self.hover_char_num != None:
                    # Mouse is currently hovering over this letter:
                    try:
                       hover_linenum, hover_line_char_num = song.songCharToLineChar(self.hover_char_num)
                    except RuntimeError:
                       print 'failed to find hover char:', self.hover_char_num
                       continue
                    if hover_linenum == linenum:
                        letter_left = line_left + self.lyrics_font_metrics.width( line_text[:hover_line_char_num] )
                        letter_right = line_left + self.lyrics_font_metrics.width( line_text[:hover_line_char_num+1] )
                        
                        # Draw a selection rectangle:
                        painter.fillRect(letter_left, lyrics_top, letter_right-letter_left, lyrics_bottom-lyrics_top, hover_brush)
                
                if self.selected_char_num != None:
                    selected_linenum, selected_line_char_num = song.songCharToLineChar(self.selected_char_num)
                    if selected_linenum == linenum:
                        letter_left = line_left + self.lyrics_font_metrics.width( line_text[:selected_line_char_num] )
                        letter_right = line_left + self.lyrics_font_metrics.width( line_text[:selected_line_char_num+1] )
                
                        # Draw a selection rectangle:
                        painter.fillRect(letter_left, lyrics_top, letter_right-letter_left, lyrics_bottom-lyrics_top, selection_brush)

            
            painter.setFont(self.lyrics_font)
            line_right = line_left + self.lyrics_font_metrics.width(line_text)
            painter.drawText(line_left, lyrics_top, line_right-line_left, lyrics_bottom-lyrics_top, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, line_text)

            painter.setFont(self.chord_font)


            for song_char_num, chord in song.all_chords.iteritems():
                chord_linenum, line_char_num = song.songCharToLineChar(song_char_num)
                if chord_linenum != linenum:
                    continue

                letter_left = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num] )
                letter_right = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num+1] )
                chord_middle = (letter_left + letter_right) / 2 # Average of left and right
                
                chord_text = chord.getChordString()
                chord_width = self.chord_font_metrics.width(chord_text)
                chord_left = chord_middle - (chord_width/2)
                chord_right = chord_middle + (chord_width/2)
                
                if draw_markers:
                    if song_char_num == self.hover_char_num:
                        # Draw a hover rectangle:
                        painter.fillRect(chord_left, chords_top, chord_right-chord_left, chords_bottom-chords_top, hover_brush)
                    
                    if song_char_num == self.selected_char_num:
                        # Draw a selection rectangle:
                        painter.fillRect(chord_left, chords_top, chord_right-chord_left, chords_bottom-chords_top, selection_brush)
                    
                painter.drawText(chord_left, chords_top, chord_right-chord_left, chords_bottom-chords_top, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, chord_text)
            
            

    
    def determineClickedLetter(self, x, y):
        """
        Determine where the specified (local) mouse coordinates position.
        That is, which lyric or chord letter was the mouse above when this
        event happened.
        """
        
        if not self.current_song:
            return None

        line_left = 20
        
        for linenum in range(self.current_song.getNumLines()):
            line_text = unicode( self.current_song.getLineText(linenum) )
            
            chords_top, chords_bottom, lyrics_top, lyrics_bottom = self.getLineHeights(linenum)
            
            if y < chords_top or y > lyrics_bottom:
                continue # Not this line
            
            #print 'mouse event on line:', linenum
            
            # Figure out the lyric letter for the mouse location:
            song_char_num = -1
            for line_char_num in range(len(line_text)):
                left = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num] )
                right = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num+1] )
                if x > left and x < right:
                    song_char_num = self.current_song.lineCharToSongChar(linenum, line_char_num)
                    break
            
            #print 'song_char_num:', song_char_num
            
            if y < chords_bottom:
                is_chord = True
                
                # Figure out if a chord is attached to this letter:
                for chord_song_char_num, chord in self.current_song.all_chords.iteritems():
                    chord_linenum, line_char_num = self.current_song.songCharToLineChar(chord_song_char_num)
                    if chord_linenum != linenum:
                        continue

                    # Figure out the y position where the should be drawn:
                    letter_left = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num] )
                    letter_right = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num+1] )

                    chord_middle = (letter_left + letter_right) / 2 # Average of left and right
                    
                    chord_text = chord.getChordString()
                    chord_width = self.chord_font_metrics.width(chord_text)
                    chord_left = chord_middle - (chord_width/2)
                    chord_right = chord_middle + (chord_width/2)
                    
                    if x > chord_left and x < chord_right:
                        chord_song_char_num = self.current_song.lineCharToSongChar(linenum, line_char_num)
                        # Location is on an existing chord
                        return (is_chord, linenum, line_char_num, chord_song_char_num)
                
                # Location is NOT on an existing chord
                if song_char_num == -1:
                    #print 'exit1'
                    return None

                #print 'event in a chord'
                return (is_chord, None, None, song_char_num)
            
            
            elif y > lyrics_top:
                # Location is above a lyric letter
                is_chord = False
                if song_char_num == -1:
                    #print 'exit2'
                    return None
                
                #print 'event in a letter'
                return (is_chord, None, None, song_char_num)
                #for line_char_num in range(len(line_text)):
                #    left = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num] )
                #    right = line_left + self.lyrics_font_metrics.width( line_text[:line_char_num+1] )
                #    if x > left and x < right:
                #        song_char_num = self.current_song.lineCharToSongChar(linenum, line_char_num)
                #        return (is_chord, linenum, line_char_num, song_char_num)
        
        #print 'exit3'
        return None

        
    
    def processSongCharEdit(self, song_char_num):
        """
        Bring up a dialog that will allow the user to add/modify the chord at
        the specified position.
        """
        
        # Check whether this character already has a chord:
        song_id = self.current_song.id
        for row in self.execute("SELECT id, character_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses FROM song_chord_link WHERE song_id=%i AND character_num=%i" % (song_id, song_char_num)):
            #id = row[0]
            note_id = row[2]
            chord_type_id = row[3]
            bass_note_id = row[4]
            marker = row[5]
            in_parentheses = row[6]
            
            chord = SongChord(self, song_id, song_char_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses)
        else:
            # New chord
            chord = SongChord(self, song_id, song_char_num, 0, 0, -1, "", False)
            
        modified_chord = ChordDialog(self).display(note_id, chord_type_id, bass_note_id)
        
        if modified_chord:
            # Ok pressed
            note_id = modified_chord.note_id
            chord_type_id = modified_chord.chord_type_id
            bass_note_id = modified_chord.bass_note_id
            marker = modified_chord.marker
            in_parentheses = modified_chord.in_parentheses
            
            # Check whether this character already has a chord, if so, alter it:
            for row in self.execute("SELECT id FROM song_chord_link WHERE song_id=%i AND character_num=%i" % (song_id, song_char_num)):
                # Replacing exising chord
                id = row[0]
                self.execute('UPDATE song_chord_link SET note_id=%i, chord_type_id=%i, bass_note_id=%i, marker="%s", in_parentheses=%i WHERE id=%i' % (note_id, chord_type_id, bass_note_id, marker, in_parentheses, id))
            else:
                # Adding a new chord
                row = self.execute("SELECT MAX(id) from song_chord_link").fetchone()
                id = row[0] + 1
                
                self.execute('INSERT INTO song_chord_link (id, song_id, character_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses) " + \
                            "VALUES (%i, %i, %i, %i, %i, %i, "%s", %i)' % (id, song_id, song_char_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses))
            self.updateCurrentSongFromDatabase()
                

    
    def getLineHeights(self, linenum):
        """
        Returns top & bottom y positions of the chords and lyrics texts
        for the specified line.
        """
        lyrics_height = self.lyrics_font_metrics.height()
        
        chords_height = self.chord_font_metrics.height()
        
        line_height = lyrics_height + chords_height
        line_height *= 0.9 # So that there is less spacing between the chords and the text
        
        line_top = linenum * line_height

        chords_top = line_top
        chords_bottom = chords_top + chords_height
        lyrics_bottom = line_top + line_height
        lyrics_top = lyrics_bottom - lyrics_height

        
        return chords_top, chords_bottom, lyrics_top, lyrics_bottom
    
    


    def importFromText(self):
        """
        Lets the user select a text file to import.
        """
        text_file = QtGui.QFileDialog.getOpenFileName(self.ui,
                    "Select a text file to import",
                    ".", # initial dir
                    "Text format (*.txt)",
        )
        if text_file: 
            text = open(text_file).read()
            # Decode UTF-8 into Unicode:
            text = text.decode('utf-8')
            self.importSongFromText(text)
    
    
    def importSongFromText(self, input_text):
        """
        Adds the song specified with the given text to the database.
        input_text should contain all lines, decoded, in Unicode.
        """

        # Key: note text, value: note ID
        self.note_text_id_dict = {}

        for row in self.execute("SELECT id, text, alt_text FROM notes"):
            #print 'row:', row
            id = row[0]
            text = row[1]
            alt_text = row[2]
            
            self.note_text_id_dict[text] = id
            self.note_text_id_dict[alt_text] = id

            
        # Key: chord type text, value: chord type ID
        self.chord_type_texts_dict = {}

        for row in self.execute("SELECT id, print FROM chord_types"):
            #print 'row:', row
            id = row[0]
            print_text = row[1]

            self.chord_type_texts_dict[print_text] = id
            if print_text == 'sus4':
                self.chord_type_texts_dict['sus'] = id
            
        
        song_text = input_text.split('\n')
        song_num = -1
        song_title = ""
        
        
        print '\n\nSONG', song_num, song_title.encode('utf-8')


        song_lines = [] # each item is a tuple of line text and chord list.
        
        
        prev_chords = []
        for line in song_text:
            
            # Attempt to convert the line to chords:
            num_chords = 0
            num_non_chords = 0
            
            tmp_chords = []
            tmp_warnings = []
            
            char_num = 0
            for word in line.split():
                if word == u'/':
                    num_chords += 1
                    converted_chord = None
                else:
                    try:
                        converted_chord = self.convertChordFromString(word)
                    except ValueError, err:
                        tmp_warnings.append( 'WARNING: %s CHORD "%s"' % (str(err), word.encode('utf-8')) )
                        num_non_chords += 1
                    else:
                        num_chords += 1
                        # FIXME align the chords instead of just putting 5 space
                        # character between them!
                        tmp_chords.append(converted_chord)
                        char_num += 6
                

            
            #print '\nnum_chords:', num_chords, 'num_non_chords:', num_non_chords
            if num_chords > num_non_chords:
                #print 'CHORD LINE:', line.encode('utf-8')
                # This is a chords line
                prev_chords = tmp_chords
                for warning_str in tmp_warnings:
                    print '  ', warning_str
            else:
                #print 'LYRICS LINE:', line.encode('utf-8')
                # This is a lyrics line
                if prev_chords:
                    chord_spacing = len(line) / len(prev_chords)
                    print 'line length:', len(line), 'chord_spacing:', chord_spacing
                    
                    # Space out the chords:
                    chords_dict = {}
                    for i, chord in enumerate(prev_chords):
                        chords_dict[i*chord_spacing] = chord
                    song_lines.append( (line, chords_dict) )
                else:
                    # The line before was NOT a chords line - no chords for this lyrics line
                    song_lines.append( (line, {}) )
                prev_chords = []
        

        global_song_text = ""
        global_song_chords = {} # key: position in the global_song_text
        
        # Print all lines for this song:
        line_start_char_num = 0
        for lyrics, chords_dict in song_lines:
            #print '  ', chords_dict
            #print lyrics.encode('utf-8')
            
            global_song_text += lyrics + '\n'
            for line_char_num, chord in chords_dict.iteritems():
                song_char_num = line_char_num + line_start_char_num
                global_song_chords[song_char_num] = chord
            
            line_start_char_num += len(lyrics) + 1 # 1 for the EOL character
        
        
        print 'IMPORTING'
        
        song_id = 0
        for row in self.execute("SELECT MAX(id) from songs"):
            song_id = row[0] + 1
        print 'song_id:', song_id
        print 'song_num:', song_num
        print 'song_title:', song_title.encode('utf-8')
        
        # Replace all double quotes with single quotes:
        global_song_text = global_song_text.replace('"', "'")

        self.execute("INSERT INTO songs (id, number, text, title) " + \
            'VALUES (%i, %i, "%s", "%s")' % (song_id, song_num, global_song_text, song_title))
        
        for song_char_num, chord in global_song_chords.iteritems():
            (marker, note_id, type_id, bass_id, in_parentheses) = chord
            if not marker:
                marker = ""
            
            in_parentheses = int(in_parentheses)
            
            # Get the next available ID:
            chord_id = 0
            for row in self.execute("SELECT MAX(id) from song_chord_link"):
                chord_id = row[0] + 1
            
            self.execute('INSERT INTO song_chord_link (id, song_id, character_num, note_id, chord_type_id, bass_note_id, marker, in_parentheses) ' + \
                        'VALUES (%i, %i, %i, %i, %i, %i, "%s", %i)' % (chord_id, song_id, song_char_num, note_id, type_id, bass_id, marker, in_parentheses))
        
        self.curs.commit()
        print 'DONE', out
        
        # Update the song table from database:
        self.updateFromDatabase()
        
        self.ui.songs_view.selectRow( self.songs_model.rowCount()-1 )


    def convertChordFromString(self, chord_str):
        """
        Convert the specified chord string to a note_id, chord_type_id, and a bass_note_id.
        """
        
        input_chord_str = chord_str[:]
        
        # FIXME
        in_parentheses = chord_str.startswith('(') and chord_str.endswith(')')
        if in_parentheses:
            chord_str = chord_str[1:-1]
        
        marker = None
        
        colon = chord_str.find(':')
        if colon != -1:
            if colon == len(chord_str)-1:
                raise ValueError("Not a chord (nothing after a colon")
                #print 'WARNING not a chord (nothing after a colon):', chord_str.encode('utf-8')
                #print '  INPUT CHORD:', input_chord_str.encode('utf-8')
                #return None
            
            marker = chord_str[:colon]
            chord_str = chord_str[colon+1:]
        
        #if marker:
        #    print 'MARKER:', marker.encode('utf-8')
        
        slash = chord_str.find('/')
        if slash != -1:
            bass = chord_str[slash+1:]
            chord_str = chord_str[:slash]
        else:
            bass = None
        
        if chord_str[0] == u'Е': # Russian letter
            chord_str = 'E' + chord_str[1:]
        if chord_str[0] == u'С': # Russian letter
            chord_str = 'C' + chord_str[1:]
        if chord_str[0] == u'В': # Russian letter
            chord_str = 'B' + chord_str[1:]
        if chord_str[0] == u'А': # Russian letter
            chord_str = 'A' + chord_str[1:]

        #print 'chord_str after bass removal:', chord_str.encode('utf-8')
        if chord_str[0] in [u'A', u'B', u'C', u'D', u'E', u'F', u'G']:
            if len(chord_str) > 1 and chord_str[1] in [u'#', u'b', u'♭', u'♯']:
                note = chord_str[:2]
                type = chord_str[2:]
            else:
                note = chord_str[0]
                type = chord_str[1:]
        else:
            raise ValueError("First chord letter is not a note")
            #print 'WARNING first chord letter is not a note:', chord_str.encode('utf-8')
            #print '  INPUT CHORD:', input_chord_str.encode('utf-8')
            #return None
        
        #print '      ', note, '  ', type, '  ', bass

        if len(note) > 1:
            if note[1] == u'#':
                note = note[0] + u'♯'
            elif note[1] == u'b':
                note = note[0] + u'♭'
        if bass and len(bass) > 1:
            if bass[1] == u'#':
                bass = bass[0] + u'♯'
            elif bass[1] == u'b':
                bass = bass[0] + u'♭'
        
        #if bass:
        #    print 'converting:', note.encode('utf-8'), type, bass.encode('utf-8')
        #else:
        #    print 'converting:', note.encode('utf-8'), type, 'None'

        note_id = self.note_text_id_dict[note]
        if bass != None:
            bass_id = self.note_text_id_dict[bass]
        else:
            bass_id = -1
        
        try:
            type_id = self.chord_type_texts_dict[type]
        except KeyError:
            raise ValueError("Unkown chord type")
            #print 'WARNING: unknown chord type:', type.encode('utf-8')
            #print '  INPUT CHORD:', input_chord_str.encode('utf-8')
            #return None
        
        return (marker, note_id, type_id, bass_id, in_parentheses)

        #print '  note:', note_id
        #print '  type:', type_id
        #print '  bass:', bass_id






# Main event loop:

qapp = QtGui.QApplication(sys.argv)
window = App()
window.ui.show()
window.ui.raise_()
sys.exit(qapp.exec_())


