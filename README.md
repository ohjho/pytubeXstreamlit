# [pytube](https://python-pytube.readthedocs.io/en/latest/index.html)X[streamlit](https://www.streamlit.io/)

streamlit app to download YouTube Videos using [pytube](https://python-pytube.readthedocs.io/en/latest/index.html)

deployed using [streamlit share](https://www.streamlit.io/sharing) to this demo: [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/ohjho/pytubexstreamlit/main)

Download video hosted by [file.io](https://www.file.io/)

## To run locally
Clone the `dev` branch by:
```
git clone --depth 1 https://github.com/ohjho/pytubeXstreamlit.git -b dev
```
and make sure you `install -r requirements.txt`

## To Do
* ~~since v0.88.0 Streamlit support [`download_button`](https://docs.streamlit.io/library/api-reference/widgets/st.download_button) which could be useful for files >100mb but this takes up RAM on the server side~~
   * this is implemented on `dev` branch
* Add option to convert video to Audio (mp3) internally (see [here](https://towardsdatascience.com/neural-style-transfer-for-audio-in-pytorch-e1de972b1f68))
