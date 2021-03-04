import requests
import pandas as pd
from datetime import date, datetime
from django.conf import settings
from django.shortcuts import render,redirect

def index(request):
    videos=[]
    if request.method == 'POST':

        search_url='https://www.googleapis.com/youtube/v3/search'
        video_url='https://www.googleapis.com/youtube/v3/videos'
        channel_url='https://www.googleapis.com/youtube/v3/channels'

        out={'id':[],
        'url':[],
        'channelId':[],
        'name':[],
        'title':[],
        'date':[],
        'thumbnail':[],
        'duration':[],
        'view':[],
        'like':[],
        'dislike':[],
        'comment':[]
        }
        subs={'channelId':[],'subscribers':[]}

        search_params = {
        'part':'snippet',
        'maxResults':50,
        'type':'video',
        'key':settings.YOTUBE_DATA_API_KEY,
        'q':request.POST['search']
        }

        r = requests.get(search_url, params=search_params)
        results = r.json()['items']
        
        videoIds=[]
        channelIds=[]
        for result in results:
            videoIds.append(result['id']['videoId'])
            channelIds.append(result['snippet']['channelId'])
            out['url'].append(f"https://www.youtube.com/watch?v={result['id']['videoId']}")
            out['id'].append(result['id']['videoId'])
            out['channelId'].append(result['snippet']['channelId'])

        if request.POST['submit'] == 'lucky':
            return redirect(f"https://www.youtube.com/results?search_query={request.POST['search']}")  

        video_params = {
            'part':'snippet,ContentDetails',
            'key':settings.YOTUBE_DATA_API_KEY,
            'id':','.join(videoIds),
            'maxResults':50
        }
        
        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        
        for result in results:
            out['date'].append(result['snippet']['publishedAt'].split("T")[0])
            out['title'].append(result['snippet']['title'])
            out['thumbnail'].append(result['snippet']['thumbnails']['high']['url'])
            out['name'].append(result['snippet']['channelTitle'])
            out['duration'].append(result['contentDetails']['duration'][2:])

        stat_params = {
            'part':'snippet,statistics',
            'key':settings.YOTUBE_DATA_API_KEY,
            'id':','.join(videoIds)
            }

        r = requests.get(video_url, params=stat_params)
        results = r.json()['items']
        
        for result in results:
            out['view'].append(result['statistics']['viewCount'])
            try:
                out['like'].append(result['statistics']['likeCount'])
                out['dislike'].append(result['statistics']['dislikeCount'])
            except:
                out['like'].append(1)
                out['dislike'].append(1)
                
        for result in results:
            try:
                out['comment'].append(result['statistics']['commentCount'])
            except:
                out['comment'].append(1)
                
        channel_params = {
        'part':'snippet, statistics',
        'key':settings.YOTUBE_DATA_API_KEY,
        'id':','.join(channelIds)
        }
        
        r = requests.get(channel_url, params=channel_params)
        results = r.json()['items']

        for result in results:
            subs['channelId'].append(result['id'])
            if result['statistics']['hiddenSubscriberCount']==False:
                subs['subscribers'].append(result['statistics']['subscriberCount'])
            else:
                subs['subscribers'].append(1)

        out=pd.DataFrame(out)
        subs=pd.DataFrame(subs)
        df= pd.merge(out,subs)

        df['date']=pd.to_datetime(df['date'])
        df['deltaDays']=df['date'].apply(lambda x: datetime.today()-x)    
        cols=['view','like','dislike','comment','subscribers']

        for col in cols:
            df[col]=pd.to_numeric(df[col])
        
        df=df.loc[(df['subscribers']>1000)]
            
        df['view_by_sub']=df['view']/df['subscribers']
        df['like_ratio']=(df['like']-df['dislike'])/(df['like']+df['dislike'])
        df['interaction_by_view']=(df['like']+df['dislike']+df['comment'])/df['view']
        df['deltaDays']=df['deltaDays'].apply(lambda x: str(x).split(" ")[0])
        df['deltaDays']=pd.to_numeric(df['deltaDays'])
        df['deltaDays']=df['deltaDays'].apply(lambda x: x+1)
        df['like_by_view']=df['like']/df['view']
        df['view_by_days']=df['view']/df['deltaDays']
        df['like_by_days']=df['like']/df['deltaDays']

        weightings = pd.Series(
        {
        "view_by_sub":0.3,
        "like_ratio":0.3,
        "interaction_by_view":0.2,
        "like_by_view":0.1,
        "like_by_days":0.05,
        "view_by_days":0.05
        })

        df['finalScore']=(df[weightings.index]*weightings).sum(axis=1)

            
        final=df.sort_values(by='finalScore',ascending=False).head(9)
        tmp=final[['title','id','url','duration','thumbnail']]
        videos=tmp.to_dict(orient='records')

    context = {
    'videos' : videos
    }

    
    return render(request, 'search/index.html', context)