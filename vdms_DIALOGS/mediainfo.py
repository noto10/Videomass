# -*- coding: UTF-8 -*-

#########################################################
# Name: mediainfo.py
# Porpose: show ffprobe info for media files
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (02) 14/03/2015
# Rev (02) 20/04/2015
# Rev (04) 27/04/2015
#########################################################

import wx
import os
import webbrowser
from vdms_IO.IO_tools import FFProbe

class Mediainfo(wx.Dialog):
    """
    Show dialog for display metadata info. 
    """
    def __init__(self, title, path, helping, ffprobe_link):
        # with 'None' not depend from videomass2. With 'parent, -1' if close
        # videomass2 also close mediainfo window:
        #wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        self.helping = helping
        
        notebook_1 = wx.Notebook(self, wx.ID_ANY)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY)
        format_info = wx.ListCtrl(notebook_1_pane_1, wx.ID_ANY,
                                  style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                  )
        sizer_format_content_staticbox = wx.StaticBox(notebook_1_pane_1, 
                                                      wx.ID_ANY, 
                                  ("FFprobe metadata FORMAT:"))
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        
        streams_info = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY,
                                   style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                   )
        sizer_stream_content_staticbox = wx.StaticBox(notebook_1_pane_2, 
                                                      wx.ID_ANY, 
                        ("FFprobe Metadata STREAMS:"))
        
        #button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(title)
        format_info.SetMinSize((640, 300))
        format_info.SetBackgroundColour(wx.Colour(217, 255, 255))
        format_info.InsertColumn(0, 'Type', width=200)
        format_info.InsertColumn(1, 'Parameters', width=450)
        streams_info.SetMinSize((640, 300))
        streams_info.SetBackgroundColour(wx.Colour(217, 255, 255))
        streams_info.InsertColumn(0, 'Type', width=200)
        streams_info.InsertColumn(1, 'Parameters', width=450)
        
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_buttons = wx.GridSizer(1, 1, 0, 0)
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_stream_content_staticbox.Lower()
        sizer_stream_content = wx.StaticBoxSizer(sizer_stream_content_staticbox, wx.VERTICAL)
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_format_content_staticbox.Lower()
        sizer_format_content = wx.StaticBoxSizer(sizer_format_content_staticbox, wx.VERTICAL)
        sizer_format_content.Add(format_info, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        sizer_tab1.Add(sizer_format_content, 1, wx.ALL | wx.EXPAND, 15)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        sizer_stream_content.Add(streams_info, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        sizer_tab2.Add(sizer_stream_content, 1, wx.ALL | wx.EXPAND, 15)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        notebook_1.AddPage(notebook_1_pane_1, ("General Informations"))
        notebook_1.AddPage(notebook_1_pane_2, ("Extensive Report"))
        grid_sizer_1.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 15)
        #grid_buttons.Add(button_help, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
        grid_buttons.Add(button_close, 0, wx.ALL, 15)
        grid_sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        
        # delete previous append:
        format_info.DeleteAllItems()
        streams_info.DeleteAllItems()
        # create instance FFProbe class:
        metadata = FFProbe(path, ffprobe_link, 'pretty') 
        # execute a control for errors:
        if metadata.ERROR():
            wx.MessageBox("[FFprobe] Error:  %s" % (metadata.error), 
                    "FFprobe - Videomass2", wx.ICON_ERROR, self)
            self.Destroy()
            return
        
        # create methods instances:
        video_list = metadata.video_stream()
        format_list = metadata.data_format()
        audio_list = metadata.audio_stream()
        subtitle_list = metadata.subtitle_stream()
                
        #populate format_info listctrl output:
        index = 0
        if format_list == []:
            print 'No FORMAT stream metadata found'
        else:
            n = len(format_list)
            for a in range(n):
                (key, value) = format_list[a][0].strip().split('=')
                num_items = format_info.GetItemCount()
                format_info.InsertStringItem(num_items, 'General format:')
                format_info.SetItemBackgroundColour(index, "yellow")
                index +=1
                for b in format_list[a]:
                    (key, value) = b.strip().split('=')
                    format_info.InsertStringItem(index, key)
                    format_info.SetStringItem(index, 1, value)
                    index += 1
        
        #populate stream_info listctrl output:
        index = 0 
        if video_list == []:
            print 'No VIDEO stream metadata found'
        else:
            n = len(video_list)
            for a in range(n):
                (key, value) = video_list[a][0].strip().split('=')
                num_items = streams_info.GetItemCount()
                streams_info.InsertStringItem(num_items, 
                               'Video media stream (index %s):' % (value[0]))
                streams_info.SetItemBackgroundColour(index, "yellow")
                index +=1
                for b in video_list[a]:
                    (key, value) = b.strip().split('=')
                    streams_info.InsertStringItem(index, key)
                    streams_info.SetStringItem(index, 1, value)
                    index += 1
                    
        if audio_list == []:
            print 'No AUDIO stream metadata found'
        else:    
            n = len(audio_list)
            for a in range(n):
                (key, value) = audio_list[a][0].strip().split('=')
                num_items = streams_info.GetItemCount()
                streams_info.InsertStringItem(num_items, 
                               'Audio media stream (index %s):' % (value[0]))
                streams_info.SetItemBackgroundColour(index, "yellow")
                index +=1
                for b in audio_list[a]:
                    (key, value) = b.strip().split('=')
                    streams_info.InsertStringItem(index, key)
                    streams_info.SetStringItem(index, 1, value)
                    index += 1
                    
        if subtitle_list == []:
            print 'No SUBTITLE stream metadata found'
        else:
            n = len(subtitle_list)
            for a in range(n):
                (key, value) = subtitle_list[a][0].strip().split('=')
                num_items = streams_info.GetItemCount()
                streams_info.InsertStringItem(num_items, 
                            'Subtitle media stream (index %s):' % (value[0]))
                streams_info.SetItemBackgroundColour(index, "yellow")
                index +=1
                for b in subtitle_list[a]:
                    (key, value) = b.strip().split('=')
                    streams_info.InsertStringItem(index, key)
                    streams_info.SetStringItem(index, 1, value)
                    index += 1
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
    #def on_help(self, event):
        #wx.MessageBox("L'help contestuale é ancora in fase di sviluppo .")
        #webbrowser.open(mediainfo_help)
        #webbrowser.open('%s/06-Informazioni_media.html' % self.helping)
        
