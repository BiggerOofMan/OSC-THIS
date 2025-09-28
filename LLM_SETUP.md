# LLM Integration Setup Guide

## 🤖 Meta Llama-3.3-70B Integration

THIS now includes AI-powered ingredient research using Meta's Llama-3.3-70B model! When the system encounters unknown ingredients not in its built-in database, it will automatically research them using the LLM and provide detailed information including:

- **Ingredient description and purpose**
- **Health concerns and safety information**  
- **Natural vs synthetic classification**
- **Potential allergen information**
- **Confidence scores for reliability**

## 🛠️ Setup Options

### Option 1: Ollama (Local - Recommended for Privacy)

**Best for: Privacy, offline usage, free operation**

1. Install Ollama from https://ollama.ai/
2. Pull the model: `ollama pull llama3.3:70b`
3. Set environment variable: `OLLAMA_HOST=http://localhost:11434`
4. Run Ollama: `ollama serve`

**Requirements:** ~40GB disk space, 16GB+ RAM recommended

### Option 2: Together AI (Cloud - Recommended for Performance)

**Best for: Performance, no local resources needed**

1. Sign up at https://api.together.xyz/
2. Get your API key from the dashboard
3. Set environment variable: `TOGETHER_API_KEY=your_api_key_here`

**Cost:** Pay per token usage

### Option 3: OpenAI-Compatible Providers

**For other cloud providers supporting Llama-3.3-70B:**

- **Groq**: Fast inference, competitive pricing
- **Fireworks AI**: Optimized for speed
- **Anyscale**: Enterprise-focused

Set environment variables:
```
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://provider-url.com/v1
LLM_MODEL_NAME=llama-3.3-70b
```

### Option 4: OpenAI Fallback

**If Llama-3.3-70B is not available:**

1. Get OpenAI API key from https://platform.openai.com/
2. Set environment variable: `OPENAI_API_KEY=sk-your_key_here`
3. Uses GPT-3.5-Turbo for research

## 📁 Configuration

1. Copy `config.env.example` to `.env`
2. Uncomment and fill in your chosen configuration
3. Load environment variables in your application

## 🚀 Usage

The LLM research happens automatically when unknown ingredients are found:

```python
from this_processor import THISProcessor

# Initialize with LLM research enabled (default)
processor = THISProcessor()

# Analyze ingredients - LLM research happens automatically
results = processor.analyze_text_directly("""
    Ingredients: Water, Methylparaben, Carrageenan, Unknown Compound XYZ
""")

# Check LLM research results
llm_info = results['llm_research_info']
print(f"Researched {llm_info['total_researched']} unknown ingredients")
```

## 📊 Results Structure

The analysis results now include:

```json
{
    "llm_research_info": {
        "total_researched": 2,
        "high_confidence_results": 1,
        "low_confidence_results": 1,
        "researched_ingredients": [
            {
                "name": "Methylparaben",
                "confidence": 0.85,
                "safety_level": "moderate",
                "natural": false,
                "purpose": "Preservative"
            }
        ],
        "research_enabled": true
    }
}
```

## 🔍 Demo

Run the demo to see LLM research in action:

```bash
python llm_demo.py
```

## ⚙️ Configuration Tips

- **Ollama**: Ensure sufficient RAM and storage space
- **Together AI**: Monitor usage to control costs
- **Custom providers**: Verify Llama-3.3-70B availability
- **Fallback**: OpenAI provides reliable but non-Llama results

## 🔐 Privacy & Security

- **Ollama**: Fully local processing, maximum privacy
- **Cloud providers**: Ingredient names sent to external APIs
- **Recommendations**: Use Ollama for sensitive applications

## 🐛 Troubleshooting

**"LLM researcher failed to initialize"**
- Check environment variables are set correctly
- Verify API keys are valid
- For Ollama, ensure service is running

**"No LLM configuration found"**
- Create `.env` file with your configuration
- Load environment variables before running

**"Low confidence results"**
- Normal for very obscure ingredients
- Cross-reference with other sources when confidence < 0.7

## 📈 Performance

- **Ollama**: 10-30 seconds per ingredient (local GPU recommended)
- **Together AI**: 1-3 seconds per ingredient  
- **OpenAI**: 2-5 seconds per ingredient

The system processes multiple unknown ingredients in parallel when possible.