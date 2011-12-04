Canape
======

Canape is an automated TV show downloader.

 * Automatically searches for new episodes with TVrage api.
 * Search video on http://thepiratebay.org/
 * Search subtitles on http://www.tvsubtitles.net/
 * Download torrent with Transmission

Install
-------

I highly recommend use of `virtualenv and virtualenvwrapper <http://www.doughellmann.com/docs/virtualenvwrapper/>`_.

To install Canape just do::

    git clone git://github.com/nduhamel/Canape.git
    cd Canape
    pip install -r requirements.txt
    pip install -e ./

Launch
------

Canape run as a daemon::

    Canape/: python runner --daemon start
    Canape/: python runner --daemon stop

If you want to start only the XML-RPC server::

    Canape/: python runner --only-xmlrpc

Using
-----

For controling Canape you need a Canape client see https://github.com/nduhamel/CanapeClient
