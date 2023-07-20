from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
import openai
import os
import tiktoken


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = "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"
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=os.environ["OPENAI_API_KEY"])
new_db = FAISS.load_local("mosip120_gitbook_04_07_faiss_index", embeddings)

app = Flask(__name__)
cors = CORS(app)
@app.route('/api', methods=['POST'])
@cross_origin()
def process_request():
    global new_db
#    apikey = request.form.get('apikey')
    prompt = request.form.get('prompt')
    context = request.form.get('context')

    # Perform your processing logic here
    # ...

    docs = new_db.similarity_search(prompt)
    delimter = "-------------------"
    sources = []
    page_content = ""

    num_t = 0
    for ds in docs:
        if num_t < 6000:
            num_t += num_tokens_from_string(ds.page_content)
            sources.append(ds.metadata['source'])
            page_content += ds.page_content + "\r\n"+delimter+"\r\n"

    messages = [{"role": "system", "content": "CONTEXT_SOURCE: "+page_content},
            {"role": "system", "content": "Provide your response only based on the provided CONTEXT_SOURCE"},
            {"role": "system", "content": "Response should not exceed 150 words. Provide steps or a table or summarize as appicable"},
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
    ]

    openai.api_key = os.environ["OPENAI_API_KEY"]

    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )
    response_message = response["choices"][0]["message"]

    # Prepare the response as a JSON object
    response = {
        'status': 'success',
        'message': response_message['content'],
        'sources': sources
        # Add any other data you want to include in the response
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
