Configuration
=============

Configuration file
------------------

The Canape configuration file location depends of the plateforme:
 * On Linux: *~/.config/canape.ini*

Default configuration file
--------------------------
::

    # Configuration file for canape
    [xmlrpc]
    start = True
    hostname = localhost
    port = 8080

    [tvshow]
    quality = 720p
    subtitles = fr
    #Interval between two check in minutes
    check_interval=1
    #Time between the air date and the moment we try to search the video (in hours)
    check_timedelta = 36

    [sources]
    #video and subtitle are list of value
    #exemple:
    #video = tpb, anothersite, etc
    video = tpb
    subtitle = tvsubtitles

    [downloader]
    #Downloader configuration
    download_dir = ~/canapedl
    [[adapters]]
    [[[transmission]]]
    address=localhost
    port=9090
    #user=None
    #password=None

Configuration directives
------------------------

[xmlrpc]
^^^^^^^^

 * **start** (*True* or *False*) define if the XML-PRC server must be started.
 * **hostname** (*hostname* or *IP*) define on which adress the server must listen.
 * **port** define on which port the server must listen.

[tvshow]
^^^^^^^^
 * **quality** (*default=720p*) quality label, define the default quality.
 * **subtitles** (*default=fr*) two letter country code, define the default subtitle language.
 * **check_interval** in minutes, define interval between two check.
 * **check_timedelta** (*default=36*) define the time between the air date and the moment when we try to search the video (in hours)

[sources]
^^^^^^^^^
 * **video** list of video sources to use
 * **subtitle** list of subtitles sources to use

[downloader]
^^^^^^^^^^^^
 * **download_dir** (*default=~/canapedl*) download destination directory



