import os

import streamlit as st
import azure.cognitiveservices.speech as speechsdk


def get_speech_config() -> speechsdk.SpeechConfig:
    key = os.getenv("SPEECH_KEY")
    region = os.getenv("SPEECH_REGION")

    if not key or not region:
        st.error("環境變數 SPEECH_KEY / SPEECH_REGION 未設定，請先在系統中設定。")
        st.stop()

    speech_config = speechsdk.SpeechConfig(
        subscription=key,
        region=region,
    )
    # 根據需求設定語言（這裡預設德語）
    speech_config.speech_recognition_language = "de-DE"
    return speech_config


def azure_stt_from_file(file_path: str) -> str:
    speech_config = get_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "⚠️ 沒有辨識到語音內容。"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        return f"❌ 辨識被取消：{cancellation.reason} - {cancellation.error_details}"
    else:
        return f"❌ 未知結果：{result.reason}"


def main():
    st.set_page_config(page_title="Azure STT Demo", layout="centered")
    st.title("Azure Speech-to-Text 語音轉文字（上傳音檔版）")

    st.markdown(
        """
        使用 Azure Speech Service 將上傳的音檔轉成文字。

        在執行本程式前，請先：
        - 安裝套件：`pip install azure-cognitiveservices-speech streamlit`
        - 在系統中設定環境變數：
          - `SPEECH_KEY`：Azure Speech 資源金鑰
          - `SPEECH_REGION`：Azure Speech 資源 region（例如：`eastasia`）
        """
    )

    uploaded_file = st.file_uploader(
        "請上傳音檔（建議 WAV / MP3）",
        type=["wav", "mp3", "ogg", "flac"],
    )

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")

        # 將上傳檔案先存到本地暫存檔再送給 Azure
        temp_path = "temp_input_audio"
        file_extension = os.path.splitext(uploaded_file.name)[1] or ".wav"
        temp_full_path = temp_path + file_extension

        with open(temp_full_path, "wb") as f:
            f.write(uploaded_file.read())

        if st.button("開始轉文字"):
            with st.spinner("Azure 正在辨識語音，請稍候…"):
                text = azure_stt_from_file(temp_full_path)

            st.subheader("辨識結果：")
            st.write(text)

            st.text_area("可編輯文字：", value=text, height=200)

            st.success("完成語音轉文字！")


if __name__ == "__main__":
    main()

