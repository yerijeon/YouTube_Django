import axios from 'axios';

export default axios.create({
    baseURL:'https://www.googleapis.com/youtube/v3',
    params: {
        part: 'snippet',
        maxResults: 5,
        key: 'AIzaSyA8fwby-2mS26q8AV8qjMxbYdTnkjHM21g'

    }
});  