import wx
from Video import *
import wx.lib.sized_controls as sc
import thread
import cv2
import datetime
import pandas as pd
#from VideoCamera import *
import threading
if "2.8" in wx.version():
    import wx.lib.pubsub.setupkwargs
    from wx.lib.pubsub import pub
else:
    from wx.lib.pubsub import pub
global t
global _FINISH
##################################################################

#-----------------------------------------------------------------------------------------------------------------------
""" This method allows the video recording from the webcam and save the video when the thread is killed """
def videorecording():
 cap = cv2.VideoCapture(0)
 # Define the codec and create VideoWriter object
 fourcc = cv2.VideoWriter_fourcc(*'XVID')
 out = cv2.VideoWriter('video.avi', fourcc, 25.0, (640, 480)) # 'video.avi is the filename, 25. is the number of frame per second, then dimension
 now = datetime.datetime.now()
 print now
 while (cap.isOpened()):

     ret, frame = cap.read()
     if ret == True:

         out.write(frame)
        # To show the video
        # cv2.imshow('frame', frame)
         if cv2.waitKey(1) & 0xFF == ord('q'):
             break

         if _FINISH:
             print now
             cap.release()
             out.release()
             cv2.destroyAllWindows()
             break
     else:
         break





########################################################################
""" Class for the Registration """

class LoginDialog(sc.SizedDialog):
    """
    Class to define login dialog
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        sc.SizedDialog.__init__(self, None,style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX |
                                                                              wx.CLOSE_BOX | wx.MINIMIZE_BOX),
                                title="Registration Form",
                                size=(400, 500))


        self.Center()
   #     self.ShowModal()
        self.SetFocus()

        panel = self.GetContentsPane()
        panel.SetSizerType("form")


        # row 1: Name
        wx.StaticText(panel, -1, "Name*")
        self.textCtrl_Name = wx.TextCtrl(panel,style=wx.TE_RICH)
        self.textCtrl_Name.SetSizerProps(expand=True)
        # row 2: Surname
        wx.StaticText(panel, -1, "Surname*")
        self.textCtrl_Surname = wx.TextCtrl(panel)
        self.textCtrl_Surname.SetSizerProps(expand=True)

        # row 3: Email
        wx.StaticText(panel, -1, "Email*")
        self.emailCtrl = wx.TextCtrl(panel)
        self.emailCtrl.SetSizerProps(expand=True)

        # row 4: Gender
        wx.StaticText(panel, -1, "Gender")
        self.Gender = wx.Choice(panel, -1, choices=["Male", "Female"])

        # row 5: Age
        wx.StaticText(panel, -1, "Age")
        self.Age = wx.Choice(panel, -1, choices=["16-20", "21-25","26-30","31-49","50-65","Over 65"])

        # row 6: Username
        wx.StaticText(panel, -1, "Username*")
        self.textCtrl_Username = wx.TextCtrl(panel, size=(60, -1))

        # row 7: Empatica ID
        wx.StaticText(panel, -1, "Empatica ID*")
        self.textCtrl_EmpaticaID = wx.TextCtrl(panel,size=(60, -1))

        # Button for the registration
        btn = wx.Button(panel, label="Register")
        btn.Bind(wx.EVT_BUTTON, self.onRegister) # when the button is clicked call the methon onSave

    # ----------------------------------------------------------------------

    """ This method save the info got from the user's login into a .csv file, invoke the camera thread
    and show the dialog box"""
    def onRegister(self, event):

        name = self.textCtrl_Name.GetValue()
        surname = [self.textCtrl_Surname.GetValue()]
        email = self.emailCtrl.GetValue()
        gender = self.Gender.GetString(self.Gender.GetSelection())
        age = self.Age.GetString(self.Age.GetSelection())
        username = self.textCtrl_Username.GetValue()
        empatica = self.textCtrl_EmpaticaID.GetValue()
        # Dataframe with all the participant's data
        df = pd.DataFrame({'Name':name,
                           'Surname': surname,
                           'Email': email,
                           'Gender': gender,
                           'Age': age,
                           'Username': username,
                           'EmpaticaID':empatica
                           })
        print df


        if (name and surname and email and username and empatica) == '':
            # if the required fields are empty prompt the login fail
            self.on_login_fail()
        else:
         # if the login is succsseful:
         # write the csv file
         df.to_csv('info.csv', index=0)

        # Start the camera thread
         t.start()

        # Show the dialog box: info uploaded
         self.on_login_success()
        # Send a message to the main frame
         pub.sendMessage("frameListener", message="show")
        # Destroy the dialog box
         self.Destroy()


    def on_login_success(self):
        wx.MessageBox('Your information have been successfully uploaded! ' 
                      'Thank you!', 'Info',
                      style = wx.OK | wx.ICON_INFORMATION & ~(wx.CLOSE_BOX ))

    def on_login_fail(self):
        wx.MessageBox('Your information are not complete, please insert your data'
                      , 'Info',
                      style = wx.OK | wx.ICON_ERROR & ~(wx.CLOSE_BOX ))

########################################################################
class MyPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)


########################################################################
class MainFrame(wx.Frame):
    """"""
    """ The MainFrame is responsible for showing the video to the participant """
    # ----------------------------------------------------------------------

            # ----------------------------------------------------------------------
            # A wx.Frame widget is an important container widget
            # The wx.Frame widget is a parent widget for other widgets
    def __init__(self, parent, id, title, mplayer):
                #wx.Frame.__init__(self, parent, id, title, size=(wx.GetDisplaySize()))  # initialize the Frame object
                wx.Frame.__init__(self, parent, id, title,
                    size=(1920,1060))  # initialize the Frame object
                self.Center()
                self.panel = wx.Panel(self)
                pub.subscribe(self.myListener, "frameListener")

                # Ask user to login
                dlg = LoginDialog()
                dlg.ShowModal()
                sp = wx.StandardPaths.Get()
                self.currentFolder = sp.GetDocumentsDir()
                self.currentVolume = 50

                self.create_menu()
                # create sizers
                mainSizer = wx.BoxSizer(wx.VERTICAL)
                controlSizer = self.build_controls()
                sliderSizer = wx.BoxSizer(wx.HORIZONTAL)

                self.mplayer = mpc.MplayerCtrl(self.panel, -1, mplayer)
                self.playbackSlider = wx.Slider(self.panel, size=wx.DefaultSize)
                sliderSizer.Add(self.playbackSlider, 1, wx.ALL | wx.EXPAND, 5)

                # create volume control
                self.volumeCtrl = wx.Slider(self.panel )
                self.volumeCtrl.SetRange(0, 100)
                self.volumeCtrl.SetValue(self.currentVolume)
                self.volumeCtrl.Bind(wx.EVT_SLIDER, self.on_set_volume)
                controlSizer.Add(self.volumeCtrl, 0, wx.ALL, 5)

                # create track counter
                self.trackCounter = wx.StaticText(self.panel, label="00:00")
                sliderSizer.Add(self.trackCounter, 0, wx.ALL | wx.CENTER, 5)
               # wx.StaticText(self.panel, label="Ciao")
                # set up playback timer
                self.playbackTimer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.on_update_playback)

                mainSizer.Add(self.mplayer, 1, wx.ALL | wx.EXPAND, 5)
                mainSizer.Add(sliderSizer, 0, wx.ALL | wx.EXPAND, 5)
                mainSizer.Add(controlSizer, 0, wx.ALL | wx.CENTER, 5)
                self.panel.SetSizer(mainSizer)

                self.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
                self.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
                self.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
                self.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)

                self.Show()  # In order to display the Frame widget we have to run  the Show() method
                self.panel.Layout()


            # ----------------------------------------------------------------------
                # build the buttons for the player
    def build_btn(self, btnDict, sizer):
                """"""
                bmp = btnDict['bitmap']
                handler = btnDict['handler']

                img = wx.Bitmap(os.path.join(bitmapDir, bmp))
                btn = buttons.GenBitmapButton(self.panel, bitmap=img,
                                              name=btnDict['name'])
                btn.SetInitialSize()
                btn.Bind(wx.EVT_BUTTON, handler)
                sizer.Add(btn, 0, wx.LEFT, 3)


            # -----------------------------------------------------------------------
    def build_controls(self):
                """
                Builds the audio bar controls
                """
                controlSizer = wx.BoxSizer(wx.HORIZONTAL)

                btnData = [{'bitmap': 'player_play.png',
                            'handler': self.on_pause, 'name': 'pause'},
                           {'bitmap': 'player_stop.png',
                            'handler': self.on_stop, 'name': 'stop'}]
                for btn in btnData:
                    self.build_btn(btn, controlSizer)

                return controlSizer

            # ----------------------------------------------------------------------

    def onClose(self, event):
        """"""
        self.Close()

    def create_menu(self):
                """
                Creates a menu
                """
                menubar = wx.MenuBar()
                fileMenu = wx.Menu()
                add_file_menu_item = fileMenu.Append(wx.NewId(), "&Add Video", "Add Media File")
                exitItem = fileMenu.Append(wx.ID_EXIT, "&Stop the Experiment")
                menubar.Append(fileMenu, '&Menu')

                self.SetMenuBar(menubar)
                self.Bind(wx.EVT_MENU, self.on_add_file, add_file_menu_item)
                self.Bind(wx.EVT_MENU, self.onClose,exitItem)

            # ----------------------------------------------------------------------
    def on_add_file(self, event):
                """
                Add a Movie and start playing it
                """
                wildcard = "Media Files (*.*)|*.*"
                dlg = wx.FileDialog(
                    self, message="Choose a file",
                    defaultDir='C:/Users/user/switchdrive/LaughterExperiment-', # path to directory of the experiment
                    defaultFile="*.mp4", # extension of the file
                    wildcard=wildcard,
                    style=wx.FD_OPEN
                )
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    self.currentFolder = os.path.dirname(path[0])
                    trackPath = '"%s"' % path.replace("\\", "/")
                    self.mplayer.Loadfile(trackPath)

                    t_len = self.mplayer.GetTimeLength()
                    self.playbackSlider.SetRange(0, t_len)
                    self.playbackTimer.Start(100)

            # ----------------------------------------------------------------------
    def on_media_started(self, event):
                print 'Media started!'

            # ----------------------------------------------------------------------
    def on_media_finished(self, event):
                print 'Media finished!'
                self.playbackTimer.Stop()

            # ----------------------------------------------------------------------
    def on_pause(self, event):
                """"""
                if self.playbackTimer.IsRunning():
                    print "pausing..."
                    self.mplayer.Pause()
                    self.playbackTimer.Stop()
                else:
                    print "unpausing..."
                    self.mplayer.Pause()
                    self.playbackTimer.Start()
                # _FINISH = True
                # t.join()

            # ----------------------------------------------------------------------
    def on_process_started(self, event):
                print 'Process started!'

            # ----------------------------------------------------------------------
    def on_process_stopped(self, event):
                print 'Process stopped!'
                self.Destroy()


           # ----------------------------------------------------------------------
    def on_set_volume(self, event):
                """
                Sets the volume of the music player
                """
                self.currentVolume = self.volumeCtrl.GetValue()
                self.mplayer.SetProperty("volume", self.currentVolume)

            # ----------------------------------------------------------------------
    def on_stop(self, event):
                """"""
                print "stopping..."
                self.mplayer.Stop()
                self.playbackTimer.Stop()



            # ----------------------------------------------------------------------
    def on_update_playback(self, event):
                """
                Updates playback slider and track counter
                """
                try:
                    offset = self.mplayer.GetTimePos()
                except:
                    return
                print offset
                mod_off = str(offset)[-1]
                if mod_off == '0':
                    print "mod_off"
                    offset = int(offset)
                    self.playbackSlider.SetValue(offset)
                    secsPlayed = time.strftime('%M:%S', time.gmtime(offset))
                    self.trackCounter.SetLabel(secsPlayed)

    # ----------------------------------------------------------------------
    def myListener(self, message, arg2=None):
        """
        Show the frame
        """
        self.Show()


if __name__ == "__main__":
    # variable shared with the camera thread, when the user quits the experiment this variable is changed to True and
    #interrupt the video camera thread
    _FINISH = False


    app = wx.App(False)
    t = threading.Thread(target=videorecording)
    frame = MainFrame(None, -1, 'Laughter Experiment', 'C:\Users\user\switchdrive\LaughterExperiment-\MPlayer\mplayer.exe')
    app.MainLoop()
    _FINISH = True
    t.join()