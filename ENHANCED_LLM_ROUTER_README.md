# Enhanced LLM Router System Documentation

## 🚀 Overview

The Enhanced LLM Router is a sophisticated routing system that intelligently distributes summarization tasks across 5 different AI APIs with specialized features for multi-language support and complex content analysis.

## 🏗️ Architecture

### Core Components

1. **ChunkComplexityAnalyzer** - Analyzes text complexity and language
2. **SmartAPIManager** - Manages API usage and load balancing  
3. **LLMRoutingEngine** - Core routing logic and execution
4. **EnhancedAgenticSummarizer** - Agentic summarization with router integration

## 🔧 API Configuration

### Supported APIs

| API | Priority | Daily Limit | Best For | Language Support |
|-----|----------|-------------|----------|------------------|
| Google Gemma (Primary) | 1 | 45 calls | All content, Indic scripts | ✅ Hindi/Urdu/Bengali |
| Google Gemma (Secondary) | 2 | 45 calls | Backup for primary | ✅ Hindi/Urdu/Bengali |  
| GROQ | 3 | 14,000 calls | High volume, simple content | ❌ English only |
| Together AI | 4 | 50 calls | Complex analysis | ❌ English only |
| OpenRouter | 5 | 180 calls | Fallback option | ❌ English only |

### Environment Setup

```bash
# Copy template and add your API keys
cp .env.template .env

# Add your API keys
GOOGLE_API_KEY=your_primary_google_api_key
GOOGLE_API_KEY_2=your_secondary_google_api_key  
GROQ_API_KEY=your_groq_api_key
TOGETHER_AI_API_KEY=your_together_ai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

## 📊 Routing Logic

### Priority-Based Routing

1. **Language Detection**
   - Hindi/Urdu/Bengali content → **Google APIs only**
   - Other languages → **Smart routing**

2. **Complexity Analysis**
   - High complexity → **Google APIs preferred**
   - Medium complexity → **Balanced routing**
   - Low complexity → **Any available API**

3. **Load Balancing**
   - Tracks daily usage for each API
   - Reserves 20% capacity for emergencies
   - Automatically balances between similar APIs

## 🎯 Specialized Agents

### Agentic Processing

1. **Introduction Agent** - Handles document openings and context setting
2. **Content Agent** - Processes main content sections  
3. **Conclusion Agent** - Handles endings and summaries
4. **Synthesis Agent** - Combines all sections into final summary

## 📡 API Endpoints

### Enhanced Summarization

```bash
# Main summarization endpoint
POST /api/enhanced/summarize
{
    "chunks": ["text chunk 1", "text chunk 2"],
    "document_info": {"title": "Document Name"}
}
```

### Router Management

```bash
# Get router status
GET /api/enhanced/router/status

# Test router connectivity  
POST /api/enhanced/router/test

# Emergency reset specific API
POST /api/enhanced/router/reset/<api_name>

# System information
GET /api/enhanced/info
```

## 🔍 Monitoring & Stats

### Usage Statistics

The system provides comprehensive statistics:

- **API Usage**: Calls per API with success rates
- **Complexity Analysis**: Content difficulty distribution
- **Language Detection**: Script type identification
- **Agent Performance**: Per-agent success rates
- **Routing Decisions**: Why specific APIs were chosen

### Example Response

```json
{
    "success": true,
    "final_summary": "...",
    "processing_stats": {
        "total_chunks_processed": 5,
        "successful_chunks": 5,
        "success_rate": 100.0,
        "api_usage_breakdown": {
            "google_primary": 3,
            "groq": 2
        }
    },
    "routing_stats": {
        "available_apis": 4,
        "emergency_mode_apis": 5
    }
}
```

## ⚡ Performance Features

### Smart Optimizations

1. **Rate Limit Management**
   - Automatic delays between calls
   - Daily quota tracking
   - Emergency fallback routing

2. **Language Optimization**
   - Google APIs for Indic scripts
   - Krutidev format support
   - Script detection algorithms

3. **Error Handling**
   - Automatic API failover
   - Retry logic with exponential backoff
   - Graceful degradation

4. **Load Balancing**
   - Usage-based routing
   - Priority-aware selection
   - Emergency capacity reservation

## 🛠️ Installation & Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Environment Configuration

1. Copy `.env.template` to `.env`
2. Add your API keys
3. Configure Redis for Celery
4. Start the application

### Testing

```bash
# Test router connectivity
curl -X POST http://localhost:5000/api/enhanced/router/test

# Check system status
curl -X GET http://localhost:5000/api/enhanced/router/status
```

## 🔒 Security & Best Practices

### API Key Management

- Store keys in environment variables
- Use separate keys for development/production
- Monitor API usage regularly
- Implement key rotation policies

### Rate Limiting

- Conservative daily limits to avoid overuse
- Emergency capacity (20%) reserved
- Automatic cooldown for failed APIs
- Smart load distribution

## 🚨 Troubleshooting

### Common Issues

1. **No Available APIs**
   - Check API keys in `.env`
   - Verify network connectivity
   - Check daily usage limits

2. **Indic Script Issues**
   - Ensure Google APIs are available
   - Check language detection accuracy
   - Verify Krutidev format support

3. **High Failure Rates**
   - Review error logs
   - Check API status pages
   - Consider emergency resets

### Debug Commands

```bash
# Emergency reset all APIs
for api in google_primary google_secondary groq together_ai openrouter; do
    curl -X POST http://localhost:5000/api/enhanced/router/reset/$api
done

# Get detailed status
curl -X GET http://localhost:5000/api/enhanced/router/status
```

## 📈 Future Enhancements

### Roadmap

1. **Dynamic Rate Limiting** - Adjust limits based on usage patterns
2. **Custom Model Selection** - Per-document model optimization  
3. **Advanced Caching** - Reduce duplicate API calls
4. **Real-time Monitoring** - Dashboard for API health
5. **Auto-scaling** - Dynamic API capacity management

## 🤝 Contributing

### Development Guidelines

1. Maintain backward compatibility
2. Add comprehensive error handling
3. Include detailed logging
4. Write unit tests for new features
5. Update documentation

### Testing Strategy

- Unit tests for individual components
- Integration tests for API routing
- End-to-end tests for complete flows
- Load tests for high-volume scenarios
