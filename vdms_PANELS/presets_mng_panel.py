# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_mng_panel.py
# Porpose: ffmpeg's presets manager panel
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

# Rev (08) 04/08/2014
# Rev (09) 01/18/2015
# Rev (10) 07/03/2015
# Rev (10) 07/05/2015
# Rev (11) 09/july/2018 
#########################################################

import wx
import os
from vdms_IO.presets_manager_properties import parser_xml
from vdms_IO.presets_manager_properties import delete_profiles
from vdms_IO.presets_manager_properties import supported_formats
from vdms_SYS.os_interaction import copy_restore, copy_backup, copy_on
from vdms_IO.filedir_control import inspect
from vdms_DIALOGS import presets_addnew

array = []# all parameters of the selected profile
# this dictionary content all presets in ~/.videomass2:
dict_presets = {
"Audio Conversions" : ("preset-v1-Audio", "Audio Conversions"), 
"Extract audio from video": ("preset-v1-VideoAudio", "Extract audio from video"),
"Convert to AVI" : ("preset-v1-AVI", "Convert to AVI"),
"Mobile Phones multimedia" : ("preset-v1-MobilePhones", "Mobile Phones multimedia"),
"iPod iTunes" : ("preset-v1-iPod-iTunes", "iPod iTunes"),
"Convert to VCD (mpg)" : ("preset-v1-VCD", "Convert to VCD (mpg)"),
"Convert DVD VOB" : ("preset-v1-VOB", "Convert DVD VOB"),
"Convert to quicktime (mov)" : ("preset-v1-quicktime", "Convert to quicktime (mov)"),
"Convert to DV" : ("preset-v1-DV", "Convert to DV"),
"Google Android" : ("preset-v1-GoogleAndroid", "Google Android"),
"Google webm" : ("preset-v1-GoogleWebm", "Google webm"),
"DVD Conversions" : ("preset-v1-DVD", "DVD Conversions"),
"MPEG-4 Conversions" : ("preset-v1-MPEG-4", "MPEG-4 Conversions"),
"PS3 Compatible" : ("preset-v1-PS3", "PS3 Compatible"),
"PSP Compatible" : ("preset-v1-PSP", "PSP Compatible"),
"Websites" : ("preset-v1-websites", "Websites"),
"User Profiles" : ("preset-v1-Personal", "User Profiles"),
                    }
# set widget colours in some case with html rappresentetion:
azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'

class PresetsPanel(wx.Panel):
    """
    The Presets manager panel is used for the direct execution of profiles 
    with the ffmpeg commands, for editing, restoring and storing them.
    """

    def __init__(self, parent, path_srcShare, path_confdir,
                 PWD, threads, cpu_used, loglevel_type, 
                 ffmpeg_link, writeline_exec, OS):
        """
        constructor
        """
        self.path_srcShare = path_srcShare
        self.path_confdir = path_confdir
        self.PWD = PWD
        self.threads = threads
        self.cpu_used = cpu_used
        self.loglevel_type = loglevel_type
        self.ffmpeg_link = ffmpeg_link
        self.writeline_exec = writeline_exec
        self.OS = OS
        self.parent = parent
        self.file_sources = []
        self.file_destin = ''
        
        wx.Panel.__init__(self, parent, -1)

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        self.list_ctrl = wx.ListCtrl(self.panel_1, wx.ID_ANY, 
                                        style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                        )
        nb1 = wx.Notebook(self.panel_1, wx.ID_ANY, style=0)
        nb1_p1 = wx.Panel(nb1, wx.ID_ANY)
        lab_prfl = wx.StaticText(nb1_p1, wx.ID_ANY, _(u"Select a preset from "
                                                    u"the drop down:"))
        self.cmbx_prst = wx.ComboBox(nb1_p1,wx.ID_ANY, choices=[
                        (dict_presets["Audio Conversions"][1]),
                        (dict_presets["Extract audio from video"][1]),
                        (dict_presets["Convert to AVI"][1]),
                        (dict_presets["Mobile Phones multimedia"][1]),
                        (dict_presets["iPod iTunes"][1]),
                        (dict_presets["Convert to VCD (mpg)"][1]),
                        (dict_presets["Convert DVD VOB"][1]),
                        (dict_presets["Convert to quicktime (mov)"][1]),
                        (dict_presets["Convert to DV"][1]),
                        (dict_presets["Google Android"][1]),
                        (dict_presets["Google webm"][1]),
                        (dict_presets["DVD Conversions"][1]),
                        (dict_presets["MPEG-4 Conversions"][1]),
                        (dict_presets["PS3 Compatible"][1]),
                        (dict_presets["PSP Compatible"][1]),
                        (dict_presets["Websites"][1]),
                        (dict_presets["User Profiles"][1]),
                        ],
                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                        )
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        
        if self.writeline_exec == 'true':
            self.txt_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"",
                                    style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        else:
            self.txt_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"",
                                       style=wx.TE_MULTILINE | wx.TE_READONLY)
            
        #----------------------------notebook 3
        #nb1_p3 = wx.Panel(nb1, wx.ID_ANY)
        
        #self.ckbox_test = wx.CheckBox(nb1_p3, wx.ID_ANY, ("Test"))
        #self.lab_sec = wx.StaticText(nb1_p3, wx.ID_ANY, "Sec : ")
        #self.spin_ctrl_test = wx.SpinCtrl(nb1_p3, wx.ID_ANY, "", min=10,
                             #max=10000, style=wx.TE_PROCESS_ENTER
                                          #)
        #static_line_1 = wx.StaticLine(nb1_p3, wx.ID_ANY, style=wx.LI_VERTICAL)
        #-----------------------widget in test processing tab (ntbook3)
        #image1 = wx.Image(self.icon_play, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.btn_play = wx.BitmapButton(nb1_p3, -1, image1)
        #self.label_preview = wx.StaticText(nb1_p3, wx.ID_ANY, "Preview")
        #self.text_group_ext = wx.TextCtrl(nb1_p3, wx.ID_ANY, "", 
                                                  #style=wx.TE_PROCESS_ENTER
                                           #)
        #----------------------------notebook 4
        #nb1_p4 = wx.Panel(nb1, wx.ID_ANY)
        #self.btn_open = wx.Button(nb1_p4, wx.ID_OPEN, "")
        #self.text_path_open = wx.TextCtrl(nb1_p4, wx.ID_ANY, "", 
                                    #style=wx.TE_PROCESS_ENTER
                                                    #)
        #self.btn_save = wx.Button(nb1_p4, wx.ID_SAVE, "")
        #self.text_path_save = wx.TextCtrl(nb1_p4, wx.ID_ANY, "", 
                                    #style=wx.TE_PROCESS_ENTER | wx.TE_READONLY
                                                    #)
        #----------------------------notebook 4
        
        #----------------------Set Properties----------------------#
        self.cmbx_prst.SetSelection(0)
        
        #self.list_ctrl.SetBackgroundColour(azure)
        self.list_ctrl.SetToolTipString(_(u"List selection profiles"))
        self.txt_cmd.SetMinSize((430, 60))
        self.txt_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_cmd.SetToolTipString(_(u"FFmpeg command output of each selected "
                                      u"profile."))
        #----------------------------notebook 4
        #self.btn_open.SetToolTipString("Import Media (files/directory)")
        #self.text_path_open.SetMinSize((320, 21))
        #self.text_path_open.SetToolTipString("Imported path-name")
        #self.btn_save.SetToolTipString("Export Media (files/directory)")
        #self.text_path_save.SetMinSize((320, 21))
        #self.text_path_save.SetToolTipString("Exported path-name")
        #----------------------------notebook 4

        #----------------------Build Layout----------------------#
        #siz1 = wx.BoxSizer(wx.VERTICAL)
        siz1 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_siz7 = wx.GridSizer(2, 1, 0, 0)
        grd_s1 = wx.FlexGridSizer(2, 1, 0, 0)
        grd_s2 = wx.FlexGridSizer(3, 1, 0, 0)
        grd_s4 = wx.GridSizer(1, 3, 0, 0)
        grid_siz5 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_siz6 = wx.FlexGridSizer(1, 7, 0, 0)
        grd_s3 = wx.GridSizer(1, 1, 0, 0)
        #siz1.Add(self.DnD, 1, wx.EXPAND|wx.ALL, 10)########################################
        grd_s1.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        grd_s3.Add(self.txt_cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grid_siz7.Add(lab_prfl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_siz7.Add(self.cmbx_prst, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        nb1_p1.SetSizer(grid_siz7)
        nb1_p2.SetSizer(grd_s3)
        
        
        #grid_siz6.Add(self.ckbox_test, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz6.Add(self.lab_sec, 0, wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz6.Add(self.text_secondi, 0, wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz6.Add(self.spin_ctrl_test, 0, wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz6.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 15)
        #grid_siz6.Add(self.btn_play, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz6.Add(self.label_preview, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_siz6.Add(self.text_group_ext, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)
        
        #nb1_p3.SetSizer(grid_siz6)
        
        #----------------------------notebook 4
        #grid_siz5.Add(self.btn_open, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz5.Add(self.text_path_open, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz5.Add(self.btn_save, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #grid_siz5.Add(self.text_path_save, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        #nb1_p4.SetSizer(grid_siz5)
        #----------------------------notebook 4
        nb1.AddPage(nb1_p1, (_("Selecting Presets")))
        nb1.AddPage(nb1_p2, (_("Command Line FFmpeg")))
        #nb1.AddPage(nb1_p3, ("Export Preferences"))
        #nb1.AddPage(nb1_p4, ("Importing/Exporting"))
        grd_s2.Add(nb1, 1, wx.EXPAND, 0)
        grd_s2.Add(grd_s4, 1, wx.EXPAND, 0)
        grd_s1.Add(grd_s2, 1, wx.ALL | wx.EXPAND, 15)
        self.panel_1.SetSizer(grd_s1)
        siz1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(siz1)
        siz1.AddGrowableRow(0)
        siz1.AddGrowableCol(0)
        grd_s1.AddGrowableRow(0)
        grd_s1.AddGrowableCol(0)
        grd_s2.AddGrowableRow(0)
        grd_s2.AddGrowableCol(0)
        self.Layout()

        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_choice_profiles, self.cmbx_prst)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.Editprof, self.list_ctrl)
        self.Bind(wx.EVT_TEXT, self.enter_command, self.txt_cmd)
        #self.Bind(wx.EVT_BUTTON, self.Playtest, self.btn_play)
        
        #----------------------Create preset list----------------------#
        if array != []: # appena avvio, cancella i dati in memoria se esistono
            del array[0:5]

        self.set_listctrl() # passo l'istanza al parsing e creo la lista
    
    #-----------------------------------------------------------------------#
    def disableParent(self):
        """
        disabling the main fraim also automatically disables this panel
        """
        self.parent.Disable()
    #-----------------------------------------------------------------------#
    def enableParent(self):
        """
        Enabling the main fraim also automatically enable this panel
        """
        self.parent.Enable()
    #-----------------------------------------------------------------------#
    def reset_list(self):
        """
        Clear all memory presets and pass to set_listctrl() for 
        re-charging new. This is used when add/edit or delete profiles. 
        The list is reloaded automatically after closing the dialogs for 
        view update .
        """
        self.list_ctrl.ClearAll()
        self.txt_cmd.SetValue("")
        self.set_listctrl()
        if array != []:
            del array[0:5]
            
    def set_listctrl(self):
        """
        Make a order list of preset (Name/Descript.) from reads xml (vdms)
        """
        try:
            #self.parent.statusbar_msg('Preset Name:  %s' % ( 
                           #dict_presets[self.cmbx_prst.GetValue()][1]),None
            #)
            av_presets = dict_presets[self.cmbx_prst.GetValue()][0]
            dati = parser_xml(av_presets) # function for parsing
            
            self.list_ctrl.InsertColumn(0, _(u'Profile Name'), width=230)
            self.list_ctrl.InsertColumn(1, _(u'Description'), width=350)
            self.list_ctrl.InsertColumn(2, _(u'Output Extension Type'), width=150)
            self.list_ctrl.InsertColumn(3, _(u'Supported formats'), width=150)
            
            index = 0
            for name in sorted(dati.keys()):
                rows = self.list_ctrl.InsertStringItem(index, name)
                self.list_ctrl.SetStringItem(rows, 0, name)
                param = dati[name]
                self.list_ctrl.SetStringItem(rows, 1, param["type"])
                self.list_ctrl.SetStringItem(rows, 2, param["estensione"])
                self.list_ctrl.SetStringItem(rows, 3, param["filesupport"])
        except:
            UnboundLocalError
            wx.MessageBox(_(u"For some circumstance, the selected preset is "
                          u"corrupted. To restore the original copy at least go "
                          u"to the File menu and choose 'restore the preset "
                          u"source in use'. Note, before you make this choice, "
                          u"saved your personal settings."), "ERROR !", 
                          wx.ICON_ERROR, self)
            return
    #----------------------Event handler (callback)----------------------#
    #------------------------------------------------------------------#
    def on_choice_profiles(self, event): # combobox
        """
        Whenever change preset type in the combobox list, clear all
        in the list_ctrl and re-charge with new file xml, clear the 
        text command and delete elements of array[] if in list.
        """
        self.reset_list()
        
    #------------------------------------------------------------------#
    def on_select(self, event): # list_ctrl
        """
        When select a profile into the list_ctrl, set the parameters
        request.
        Is the main point where be filled the list_ctrl for view.
        The presets are the files with extension vdms. The profiles
        are content it on presets and are selected in list_ctrl
        """
        combvalue = dict_presets[self.cmbx_prst.GetValue()][0] # name xml
        dati = parser_xml(combvalue) # call module. All data go in dict
        if array != []:
            del array[0:5] # delete all: lista [0],[1],[2],[3],[4]
            
        slct = event.GetText() # event.GetText is a Name Profile
        self.txt_cmd.SetValue("")
        # param, pass a name profile and search all own elements in list.
        param = dati[event.GetText()] 
        # lista extract and construct command from param and description (type)
        # slct is the profile name
        lista =  [slct, param["type"],param["parametri"], param["filesupport"], 
            param["estensione"]]

        array.append(lista[0])# lista[0] is the profile name 
        array.append(lista[1])# lista[1] description
        array.append(lista[2])# lista[2] is the final command
        array.append(lista[3])# lista[3] the file support
        array.append(lista[4])# lista[4] output format name
        
        self.txt_cmd.AppendText(lista[2]) # this is cmd show in text ctrl
        
        self.parent.statusbar_msg(_(u'Pofile Name Selected:  %s') % (array[0]),
                                                                        None)

    #------------------------------------------------------------------#
    def enter_command(self, event): # text command view
        """
        If a profile is selected, append text into the text_ctrl. Also
        modified the text received signal event
        """
        self.txt_cmd.GetValue()
    #------------------------------------------------------------------#
    def exportStreams(self, exported):
        """
        Set the parent.post_process attribute for communicate it the
        file disponibilities for play or metadata functionalities.
        """
        if not exported:
            return
        else:
            self.parent.post_process = exported
            self.parent.postExported_enable()

    #------------------------------------------------------------------#
    def Saveme(self):
        """
        save a single file copy of preset. The saved presets must be have
        same name where is saved to restore it correctly
        """
        print 'saveme'
        combvalue = dict_presets[self.cmbx_prst.GetValue()][0]
        filedir = '%s%s.vdms' % (self.path_confdir, combvalue)
        filename = combvalue
        
        dialsave = wx.DirDialog(self, _(u"Select a directory to save it"))
        if dialsave.ShowModal() == wx.ID_OK:
            dirname = dialsave.GetPath()
            copy_backup(filedir, '%s/%s.vdms' % (dirname, filename))
            dialsave.Destroy()
            wx.MessageBox(_(u"The preset is saved"), "Info", wx.OK, self)
    #------------------------------------------------------------------#
    def Restore(self):
        """
        Replace the selected preset with other saved custom preset.
        """
        filename = dict_presets[self.cmbx_prst.GetValue()][0]
        filedir = '%s%s.vdms' % (self.path_confdir, filename)

        wildcard = "Source (*.vdms)|*.vdms| All files (*.*)|*.*"
        dialfile = wx.FileDialog(self, 
                                 _(u"Preset restore (%s.vdms) - Videomass2 ")
                                 % (filename), "%s" % (filename), "", 
                                 wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                     )
        if dialfile.ShowModal() == wx.ID_OK:
            dirname = dialfile.GetPath()
            tail = os.path.basename(dirname) # take a filename for valuated
            dialfile.Destroy()
            
            if tail != '%s.vdms' % filename:
                wx.MessageBox(_(u"'%s' \n\ndoes not match with the one in use:\n\n"
                              u"'%s'\n\nPlease, select a corresponding preset "
                              u"in the \ncombobox, first") % (dirname, filename), 
                              "WARNING ! - Videomass2",  wx.ICON_WARNING, self
                                )
                return
            
            if wx.MessageBox(_(u'The preset "%s" will be imported and will '
                    u'overwrite the one in use ! Proceed ?') % (tail), 
                    _(u'Please confirm - Videomass2'), wx.ICON_QUESTION | 
                                                  wx.YES_NO, 
                                                  self) == wx.NO:
                return
            
            copy_restore('%s' % (dirname), filedir)
            self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default(self):
        """
        Replace the selected preset at default values. 
        This replace new personal changes make at any profiles of the 
        selected preset.
        """ 
        #copy_restore('%s/share/av_presets.xml' % (self.PWD), '%s' % (self.dirconf))
        if wx.MessageBox(_(u"The current preset will be overwritten to "
                         u"default values! proceed?"), 
                         _(u"Please confirm - Videomass2"), wx.ICON_QUESTION | 
                         wx.YES_NO, self) == wx.NO:
            return
        
        filename = dict_presets[self.cmbx_prst.GetValue()][0]
        copy_restore('%s/%s.vdms' % (self.path_srcShare, 
                                     filename
                                     ), 
                                    '%s%s.vdms' % (self.path_confdir, 
                                                   filename))
        self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default_all(self):
        """
        restore all preset files in the path presets of the program
        """
        if wx.MessageBox(_(u"WARNING: you are going to restore all default "
                         u"presets from videomass2! Proceed?"), 
                         _(u"Please confirm - Videomass2"), 
                         wx.ICON_QUESTION | 
                         wx.YES_NO, self) == wx.NO:
            return

        copy_on('vdms', self.path_srcShare, self.path_confdir)
    #------------------------------------------------------------------#
    def Refresh(self):
        """ 
        Pass to reset_list function for re-charging list
        """
        self.reset_list()
    
    #------------------------------------------------------------------#
    def Addprof(self):
        """
        Store new profiles in the same presets selected in the
        combobox. The list is reloaded automatically after
        pressed ok button in the dialog for update view.
        """
        print 'addprof'
        filename = dict_presets[self.cmbx_prst.GetValue()][0]
        name_preset = dict_presets[self.cmbx_prst.GetValue()][1]
        full_pathname = '%s%s.vdms' % (self.path_confdir, filename)

        prstdialog = presets_addnew.MemPresets(self, 'newprofile', 
                                               full_pathname, filename, 
                                               None, _(u'Create a new '
                                u'profile on the selected "%s" preset') % (
                                                name_preset)
                                                )
        ret = prstdialog.ShowModal()
        if ret == wx.ID_OK:
            self.reset_list() # re-charging list_ctrl with newer
    #------------------------------------------------------------------#
    def Editprof(self, event):
        """
        A choice in the list (profile) can be edit in all own part.
        The list is reloaded automatically after pressed save button 
        in the dialog.
        """
        print 'editprof'
        if array == []:
            self.parent.statusbar_msg(_(u"Select a profile in the list "
                                      u"before to edit profile itself"), 
                                      yellow)
            return
        else:
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            name_preset = dict_presets[self.cmbx_prst.GetValue()][1]
            full_pathname = '%s%s.vdms' % (self.path_confdir, filename)
            
            prstdialog = presets_addnew.MemPresets(self, 'edit', 
                                                   full_pathname, 
                                                   filename, array, 
                                            _(u'Edit profile on "%s" preset: ') 
                                                   % (name_preset)
                                                   )
            ret = prstdialog.ShowModal()
            if ret == wx.ID_OK:
                self.reset_list() # re-charging list_ctrl with newer
    #------------------------------------------------------------------#
    def Delprof(self):
        """
        Delete a choice in list_ctrl. This delete only single
        profile of the preset used
        """
        print 'delprof'
        if array == []:
            self.parent.statusbar_msg(_(u"Select a profile in the list "
                                      u"before deleting profile itself"), 
                                      yellow)
        else:
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            if wx.MessageBox(_(u"Are you sure you want to delete the "
                             u"selected profile?"), 
                             _(u"Please confirm - Videomass2"), 
                             wx.ICON_QUESTION | 
                             wx.YES_NO, self) == wx.NO:
                return
        
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            # call module-function and pass list as argument
            delete_profiles(array, filename)
            self.reset_list()
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        The method composes the command strings to be sent to the 
        ffmpeg's process.
        It also involves the files existence verification procedures,
        overwriting control and log writing.
        
        """
        self.time_seq = self.parent.time_seq
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # comcheck, cut string in spaces and become list:
        comcheck = self.txt_cmd.GetValue().split()#ffmpeg command
        # used for file name log 
        logname = 'Videomass_PresetsManager.log'

        ######## ------------ VALIDAZIONI: --------------
        if array == []:
            self.parent.statusbar_msg(_(u"Select a profile in the list "
                                      u"before start encoding"), yellow)
            return
        array3, array4 = array[3], array[4]
        file_sources = supported_formats(array3, file_sources)
        checking = inspect(file_sources, dir_destin, array4)
        if not checking[0]:# l'utente non vuole continuare o files assenti
            return
        # typeproc: batch or single process
        # filename: nome file senza ext.
        # base_name: nome file con ext.
        # lenghmax: count processing cicles for batch mode
        typeproc, file_sources, dir_destin,\
        filename, base_name, lenghmax = checking

        ######## ------------FINE VALIDAZIONI: --------------
        if 'DOUBLE_PASS' in comcheck:
            
            split = self.txt_cmd.GetValue().split('DOUBLE_PASS')
            passOne = split[0].strip()
            passTwo = split[1].strip()
            
            command1 = ("-loglevel %s %s %s %s %s -f rawvideo" % (
                                                    self.loglevel_type, 
                                                    passOne, 
                                                    self.threads, 
                                                    self.cpu_used,
                                                    self.time_seq,)
                        )
            command2 = ("-loglevel %s %s %s %s %s" % (self.loglevel_type, 
                                                      passTwo, 
                                                      self.threads, 
                                                      self.cpu_used,
                                                      self.time_seq,
                                                      )
                        )
            pass1 = " ".join(command1.split())# mi formatta la stringa
            pass2 = " ".join(command2.split())# mi formatta la stringa

            self.parent.switch_Process('doublepass',
                                        file_sources, 
                                        array[4], 
                                        dir_destin, 
                                        None, 
                                        [pass1, pass2], 
                                        self.ffmpeg_link,
                                        '', 
                                        logname, 
                                        lenghmax, 
                                        )
            #used for play preview and mediainfo:
            f = os.path.basename(file_sources[0]).split('.')[0]
            self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                            array[4]))

        else:
            command = ("-loglevel %s %s "
                        "%s %s %s -y" % (self.loglevel_type, 
                                        self.txt_cmd.GetValue(), 
                                        self.threads, 
                                        self.cpu_used,
                                        self.time_seq)
                                        )
            self.parent.switch_Process('normal',
                                        file_sources, 
                                        array[4], 
                                        dir_destin, 
                                        command, 
                                        None, 
                                        self.ffmpeg_link,
                                        '', 
                                        logname, 
                                        lenghmax, 
                                        )
            f = os.path.basename(file_sources[0]).split('.')[0]
            self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                            array[4]))

