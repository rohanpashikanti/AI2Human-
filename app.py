import ssl
import re
import random
import requests
import spacy
import nltk
import language_tool_python
from flask import Flask, request, jsonify, render_template_string
from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# --- Setup SSL (if needed) ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- Download NLTK Data ---
nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('omw-1.4')

# --- Load spaCy Model ---
nlp = spacy.load('en_core_web_sm')

# --- Hugging Face API Key ---
API_KEY = "YOUR_HUGGING_FACE_API_KEY"  # Replace with your actual key
headers = {"Authorization": f"Bearer {API_KEY}"}

# --- NLP Functions ---

def paraphrase_text(text: str) -> str:
    """
    Paraphrase text using a Hugging Face model (e.g., tuner007/pegasus_paraphrase).
    """
    url = "https://api-inference.huggingface.co/models/tuner007/pegasus_paraphrase"
    payload = {
        "inputs": text,
        "parameters": {"max_length": 256, "num_beams": 10, "num_return_sequences": 1}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['generated_text'].strip()
    # Fallback: simple cleaning
    return re.sub(r"[^\w\s]", "", text)

def style_transfer_text(text: str) -> str:
    """
    Convert the paraphrased text into a friendly, human-like tone using GPT-2.
    """
    url = "https://api-inference.huggingface.co/models/gpt2"
    prompt = f"Rewrite the following text in a human-like, friendly tone. Text: {text}\n\nRewritten text:"
    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 556, "temperature": 0.8}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        generated_text = data[0].get('generated_text', '')
        if "Rewritten text:" in generated_text:
            generated_text = generated_text.split("Rewritten text:")[-1].strip()
        if generated_text:
            return generated_text
    return text

def lexical_syntax_modification(text: str) -> str:
    """
    Enhance text by replacing verbs, adjectives, and adverbs with synonyms using WordNet.
    """
    doc = nlp(text)
    modified_tokens = []
    for token in doc:
        if token.pos_ in ['VERB', 'ADJ', 'ADV']:
            synonyms = set()
            wn_pos = wordnet.VERB if token.pos_ == 'VERB' else wordnet.ADJ if token.pos_ == 'ADJ' else wordnet.ADV
            for syn in wordnet.synsets(token.text, pos=wn_pos):
                for lemma in syn.lemmas():
                    if lemma.name().lower() != token.text.lower():
                        synonyms.add(lemma.name().replace('_', ' '))
            if synonyms:
                modified_tokens.append(random.choice(list(synonyms)))
            else:
                modified_tokens.append(token.text)
        else:
            modified_tokens.append(token.text)
    return ' '.join(modified_tokens)

def sentence_variation_fluency(text: str) -> str:
    """
    Enhance readability by splitting long sentences and merging very short ones.
    """
    doc = nlp(text)
    enhanced_sentences = []
    for sent in doc.sents:
        words = [token.text for token in sent]
        if len(words) > 20:
            midpoint = len(words) // 2
            first_half = ' '.join(words[:midpoint]).strip()
            second_half = ' '.join(words[midpoint:]).strip()
            enhanced_sentences.append(first_half + '.')
            enhanced_sentences.append(second_half)
        elif len(words) < 10:
            enhanced_sentences.append(' '.join(words) + ', which is noteworthy.')
        else:
            enhanced_sentences.append(' '.join(words))
    return ' '.join(enhanced_sentences).replace(' .', '.')

def sentiment_emotion_enhancement(text: str) -> str:
    """
    Detect sentiment using VADER; if neutral, prepend expressive phrases to each sentence.
    """
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    if -0.05 < scores['compound'] < 0.05:
        doc = nlp(text)
        phrases = ["Remarkably", "Notably", "With heartfelt warmth", "With genuine enthusiasm"]
        enhanced_sentences = []
        for sent in doc.sents:
            phrase = random.choice(phrases)
            enhanced_sentences.append(f"{phrase}, {sent.text.strip()}")
        return " ".join(enhanced_sentences)
    return text

def detect_ai_text(text: str) -> float:
    """
    Dummy AI text detection function.
    """
    return 0.8

def optimize_text(text: str) -> str:
    """
    Apply final tweaks: adjust contractions, punctuation, and sentence rhythm.
    """
    optimized = text.replace(" do not ", " don't ")
    optimized = re.sub(r"\s+", " ", optimized)
    sentences = optimized.split(". ")
    optimized_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 25:
            midpoint = len(words) // 2
            sentence = " ".join(words[:midpoint]) + "; " + " ".join(words[midpoint:])
        optimized_sentences.append(sentence)
    return ". ".join(optimized_sentences)

def correct_text(text: str) -> str:
    """
    Use LanguageTool to correct spelling mistakes and punctuation.
    """
    try:
        tool = language_tool_python.LanguageTool('en-US')
        corrected_text = tool.correct(text)
        return corrected_text
    except Exception as e:
        print("Error in text correction:", e)
        return text

def apply_mode_formatting(text: str, mode: str) -> str:
    """
    Adjust the final text based on the selected mode using GPT-2.
    
    Modes:
    - Balanced:
        Tone: Friendly and accessible without being overly casual.
        Style: Clear, straightforward language that avoids jargon.
        Goal: Connect with a wide audience by maintaining warmth and clarity.
    - Professional:
        Tone: Polished and precise.
        Style: Concise, formal language with a focus on accuracy and authority.
        Goal: Present information in a clear, well-organized manner.
    - Creative:
        Tone: Imaginative and expressive.
        Style: Use vivid language, metaphors, and narrative elements.
        Goal: Evoke emotions and create a memorable experience.
    """
    mode_lower = mode.lower()
    if "balanced" in mode_lower:
        prompt = f"Rewrite the following text in a friendly and accessible tone, using clear and straightforward language that avoids jargon. The goal is to maintain warmth and clarity: {text}"
    elif "professional" in mode_lower:
        prompt = f"Rewrite the following text in a polished and precise tone. Use concise, formal language with a focus on accuracy and authority, suitable for a professional context: {text}"
    elif "creative" in mode_lower:
        prompt = f"Rewrite the following text in an imaginative and expressive tone. Use vivid language, metaphors, and narrative elements to create a memorable experience while maintaining clarity: {text}"
    else:
        return text

    url = "https://api-inference.huggingface.co/models/gpt2"
    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 556, "temperature": 0.8}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        generated_text = data[0].get('generated_text', '')
        # Remove prompt if present in output
        if prompt in generated_text:
            generated_text = generated_text.split(prompt)[-1].strip()
        return generated_text if generated_text else text
    return text

def humanize_pipeline(original_text: str, mode: str) -> dict:
    """
    Process the text through all NLP steps, then apply correction and mode formatting.
    """
    preprocessed = re.sub(r"[^\w\s]", "", original_text)
    paraphrased = paraphrase_text(original_text)
    styled = style_transfer_text(paraphrased)
    lex_modified = lexical_syntax_modification(styled)
    fluency_enhanced = sentence_variation_fluency(lex_modified)
    sentiment_enhanced = sentiment_emotion_enhancement(fluency_enhanced)
    ai_score_before = detect_ai_text(sentiment_enhanced)
    optimized = optimize_text(sentiment_enhanced)
    ai_score_after = detect_ai_text(optimized)
    final_text = correct_text(optimized)
    mode_text = apply_mode_formatting(final_text, mode)
    
    return {
        "preprocessed_text": preprocessed,
        "paraphrased_text": paraphrased,
        "style_transferred_text": styled,
        "lexical_syntax_modified_text": lex_modified,
        "fluency_enhanced_text": fluency_enhanced,
        "sentiment_enhanced_text": sentiment_enhanced,
        "optimized_text": mode_text,
        "ai_detection_score_before": ai_score_before,
        "ai_detection_score_after": ai_score_after
    }

# --- Flask App Initialization ---
app = Flask(__name__)

# --- HTML Template using Samsung AI Color Palette and Updated Features ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Text Humanizer</title>
  <style>
    /* Global reset & Samsung AI inspired color palette */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Ubuntu, Cantarell, sans-serif;
    }
    body {
      min-height: 100vh;
      background: linear-gradient(135deg, #E0F7FA, #FFFFFF);
      padding: 2rem;
      display: flex;
      justify-content: center;
      align-items: center;
      animation: fadeInPage 0.8s ease-in-out;
    }
    @keyframes fadeInPage {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .container {
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
    }
    h1 {
      text-align: center;
      color: #1428A0;
      margin-bottom: 1rem;
      font-size: 2.5rem;
    }
    .subtitle {
      text-align: center;
      color: #555;
      margin-bottom: 2rem;
      font-size: 1.1rem;
    }
    .editor-container {
      display: flex;
      gap: 2rem;
      margin-bottom: 2rem;
    }
    .editor-section {
      flex: 1;
      background: #FFFFFF;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 4px 8px rgba(20, 40, 160, 0.15);
      position: relative;
      overflow: hidden;
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
    .section-title {
      font-weight: 600;
      color: #1428A0;
    }
    textarea {
      width: 100%;
      height: 300px;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 1rem;
      font-size: 1rem;
      resize: none;
      transition: background-color 0.3s;
    }
    textarea:focus {
      border-color: #0D47A1;
      background-color: #F1F8E9;
      outline: none;
    }
    .button-container {
      display: flex;
      gap: 1rem;
    }
    .action-button {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: #F5F5F5;
      color: #333;
      transition: background-color 0.3s, transform 0.2s;
    }
    .action-button:hover {
      background: #E0E0E0;
      transform: scale(1.02);
    }
    .humanize-button {
      background: #0D47A1;
      color: white;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.3s, transform 0.2s;
    }
    .humanize-button:hover {
      background: #08306B;
      transform: scale(1.02);
    }
    .mode-select {
      padding: 0.5rem;
      border-radius: 6px;
      border: 1px solid #ddd;
    }
    .stats {
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #555;
      font-size: 0.9rem;
      margin-top: 1rem;
    }
    .word-count {
      font-weight: 500;
    }
    /* Fade in animation for updated output */
    .fade-in {
      animation: fadeIn 0.6s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @media (max-width: 768px) {
      .editor-container {
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Convert AI Text To Human With Our AI Humanizer</h1>
    <p class="subtitle">
      Instantly humanize AI text with our powerful converter. Achieve a 90% human score without fail!
    </p>
    <div class="editor-container">
      <!-- Input Section -->
      <div class="editor-section">
        <div class="section-header">
          <span class="section-title">Your Content</span>
          <div class="button-container">
            <button id="try-sample" class="action-button">👋 Try A Sample</button>
            <button id="paste-text" class="action-button">📋 Paste Text</button>
          </div>
        </div>
        <textarea id="input-text" placeholder="Enter your AI-generated text here..."></textarea>
        <div class="stats">
          <span class="word-count" id="input-word-count">0 Words</span>
          <div class="mode">
            Mode:
            <select id="mode-select" class="mode-select">
              <option>✎ Balanced</option>
              <option>🎯 Professional</option>
              <option>🎨 Creative</option>
            </select>
          </div>
        </div>
      </div>
      <!-- Output Section -->
      <div class="editor-section">
        <div class="section-header">
          <span class="section-title">Output</span>
        </div>
        <textarea id="output-text" readonly placeholder="Your humanized text will appear here..."></textarea>
        <div class="stats">
          <span class="word-count" id="output-word-count">0 Words</span>
        </div>
      </div>
    </div>
  </div>
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const inputText = document.getElementById('input-text');
      const outputText = document.getElementById('output-text');
      const trySampleButton = document.getElementById('try-sample');
      const pasteTextButton = document.getElementById('paste-text');
      const inputWordCountEl = document.getElementById('input-word-count');
      const outputWordCountEl = document.getElementById('output-word-count');
      const modeSelect = document.getElementById('mode-select');

      // Create Humanize button if not already present
      if (!document.getElementById('humanize-btn')) {
        const humanizeBtn = document.createElement('button');
        humanizeBtn.id = "humanize-btn";
        humanizeBtn.className = "humanize-button";
        humanizeBtn.textContent = "✨ Humanize";
        // Append below the input section's stats
        inputText.parentElement.parentElement.appendChild(humanizeBtn);
      }
      const humanizeButton = document.getElementById('humanize-btn');

      // Sample text for demonstration
      const sampleText = "This is an AI-generated response to your query about the benefits of exercise. Exercise has numerous health benefits including improved cardiovascular health, enhanced muscle strength, and better mental well-being.";

      trySampleButton.addEventListener('click', () => {
        inputText.value = sampleText;
        updateInputWordCount();
      });

      pasteTextButton.addEventListener('click', async () => {
        try {
          const clipboardText = await navigator.clipboard.readText();
          if (clipboardText) {
            inputText.value = clipboardText;
            updateInputWordCount();
          } else {
            alert("No text found in clipboard!");
          }
        } catch (err) {
          alert("Unable to access clipboard. Please allow clipboard permissions.");
        }
      });

      humanizeButton.addEventListener('click', async () => {
        if (!inputText.value.trim()) {
          alert("Please enter or paste some AI-generated text first.");
          return;
        }
        humanizeButton.textContent = "Humanizing...";
        humanizeButton.disabled = true;
        try {
          const response = await fetch('/humanize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: inputText.value, mode: modeSelect.value })
          });
          if (!response.ok) throw new Error("Error humanizing text");
          const result = await response.json();
          animateText(outputText, result.optimized_text || "No output received.", 25);
        } catch (err) {
          console.error(err);
          alert("There was an error processing your request.");
        }
        humanizeButton.textContent = "✨ Humanize";
        humanizeButton.disabled = false;
      });

      // Animate text letter-by-letter for smooth transition
      function animateText(element, text, speed = 30) {
        element.value = "";
        let index = 0;
        const interval = setInterval(() => {
          if (index < text.length) {
            element.value += text[index];
            index++;
          } else {
            clearInterval(interval);
            updateOutputWordCount();
          }
        }, speed);
      }

      function updateInputWordCount() {
        const words = inputText.value.trim().split(/\s+/).filter(word => word.length);
        inputWordCountEl.textContent = words.length + " Words";
      }

      function updateOutputWordCount() {
        const words = outputText.value.trim().split(/\s+/).filter(word => word.length);
        outputWordCountEl.textContent = words.length + " Words";
      }

      inputText.addEventListener('input', updateInputWordCount);
    });
  </script>
</body>
</html>
"""

# --- Routes ---

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/humanize", methods=["POST"])
def humanize():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    input_text = data["text"]
    mode = data.get("mode", "Balanced")
    result = humanize_pipeline(input_text, mode)
    return jsonify(result)

# --- Run the Flask App ---
if __name__ == "__main__":
    app.run(debug=True)
