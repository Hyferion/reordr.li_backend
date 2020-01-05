import math
import sys

import numpy as np
import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reo.Model.Track import Track
from reo.PlaylistScrambler import get_tracks_for_playlist, get_features_for_tracks, reorder_a_track


def getSimilarity(obj1, obj2):
    len1 = len(obj1.index)
    len2 = len(obj2.index)
    if not (len1 == len2):
        print("Error: Compared objects must have same number of features.")
        sys.exit()
        return 0
    else:
        similarity = obj1 - obj2
        similarity = np.sum((similarity ** 2.0) / 10.0)
        similarity = 1 - math.sqrt(similarity)
        return similarity


@api_view(['POST'])
def shuffle(request):
    if request.method == 'POST':
        try:
            access_token = request.data.get('access_token')
            playlist = request.data.get('playlist')
            ref_track = request.data.get('track')
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        list_of_parameters = ['acousticness', 'danceability', 'energy', 'instrumentalness']

        tracks = get_tracks_for_playlist(playlist, access_token)
        tracks = get_features_for_tracks(tracks, access_token)

        tracks_df = pd.DataFrame(tracks)
        tracks_df = tracks_df[list_of_parameters]

        for index, track in enumerate(tracks):
            if ref_track == track['id']:
                ref_track = track
                # del tracks[index]
                ref_track_df = tracks_df.iloc[index]

        # s = getSimilarity(tracks.iloc[0],tracks.iloc[1])
        # print(s)
        similarity_list = []
        position_counter = 0
        for track in tracks:
            track_df = pd.DataFrame(track, index=[0])
            track_df = track_df[list_of_parameters]
            track_df = track_df.iloc[0]
            track_obj = Track(id=track['id'], position=position_counter)
            s = getSimilarity(ref_track_df, track_df)
            track_obj.similiarity = s
            similarity_list.append(track_obj)
            position_counter = position_counter + 1

        print(similarity_list)
        sorted_similarity_list = sorted(similarity_list, key=lambda x: x.similiarity)
        sorted_similarity_list.reverse()
        print(sorted_similarity_list)
        save_order = sorted_similarity_list.copy()

        desired_position = 0
        for index, track in enumerate(sorted_similarity_list):
            if track.position != desired_position:
                reorder_a_track(track.position, desired_position, playlist, access_token)
                # del sorted_similarity_list[index]
            for t in sorted_similarity_list:
                if t.position >= desired_position and track.position > t.position:
                    t.position = t.position + 1
            desired_position = desired_position + 1

        return Response(status=status.HTTP_200_OK)
