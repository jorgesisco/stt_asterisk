import uuid
import ari
import logging
import sys
import requests
# from ari.exceptions import ARINotFound

from contextlib import contextmanager
from functools import partial

from app import ARI_URL, ARI_USERNAME, ARI_PASSWORD, APPLICATION

BRIDGE_ID = str(uuid.uuid4())

logging.basicConfig(level=logging.DEBUG)


@contextmanager
def application_bridge(client):
    logging.debug('Creating our bridge')
    bridge = client.bridges.createWithId(
        bridgeId=BRIDGE_ID,
        name=BRIDGE_ID,
        type='mixing',
    )
    try:
        yield bridge
    finally:
        try:
            logging.debug('Destroying our bridge')
            client.bridges.destroy(bridgeId=BRIDGE_ID)
        except exceptions:
            pass


def on_playback_finished(channel, playback, event):
    logging.debug('Playback finished, hanging up the channel.')
    channel.hangup()


def on_stasis_start(objects, event, bridge):
    logging.debug('%s', event)

    channel = objects['channel']
    channel.answer()
    channel_id = event['channel']['id']
    bridge.addChannel(channel=channel_id)

    # Play the sound and capture the returned playback object
    playback = channel.play(media="sound:/app/softphone_app/wavs/intro")

    # Attach the event listener to the playback object
    playback.on_event('PlaybackFinished', partial(on_playback_finished, channel))


def main():
    logging.debug(f'Starting {sys.argv[0]}...')
    client = ari.connect(
        base_url=ARI_URL,
        username=ARI_USERNAME,
        password=ARI_PASSWORD,
    )

    with application_bridge(client) as bridge:
        client.on_channel_event('StasisStart', partial(on_stasis_start, bridge=bridge))
        client.run(apps=[APPLICATION])


if __name__ == "__main__":
    main()
