# 🎨 StylerX - Personal Color & Fashion Intelligence Platform

**AI-Powered Personal Stylist Prototype**

A prototype platform demonstrating how AI ensemble learning can analyze personal color seasons and provide fashion recommendations using multiple state-of-the-art AI models.

## 📖 API Documentation

**Live API Documentation**: [https://stylist-ai-be.onrender.com/docs](https://stylist-ai-be.onrender.com/docs)

Interactive API documentation with Swagger UI - explore all endpoints, test requests, and view schemas.

---

## 📝 Summary

StylerX is a prototype AI-powered personal color analysis and fashion recommendation platform. It uses ensemble learning with three AI models (Gemini 2.5, GPT-4o, Claude 3.5) to analyze facial features, determine personal color seasons using the 12-season classification system, and recommend compatible fashion items. The platform demonstrates how parallel and hybrid model orchestration can achieve high accuracy in color analysis.

**This is a prototype** showcasing the project idea and implementation approach.

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- API Keys: Google Gemini, OpenAI, Anthropic Claude

### Setup

```bash
# 1. Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_jwt_secret_key_here
LOG_LEVEL=INFO
EOF

# 2. Start the service
docker-compose up -d

# 3. Access API docs
# Local: http://localhost:8000/docs
# Production: https://stylist-ai-be.onrender.com/docs
```

---

## 📚 API Routes

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Color Analysis

- `POST /api/analyze/color` - Single model color analysis (fast)
- `POST /api/analyze/color/ensemble/parallel` - Parallel ensemble (3 models analyze simultaneously)
- `POST /api/analyze/color/ensemble/hybrid` - Hybrid ensemble (2 models + 1 judge)
- `GET /api/color/palette/{season}` - Get color palette for a season

### Fashion Recommendations

- `GET /api/outfit/season/{season}` - Get outfits by color season
- `GET /api/outfit/category/{category}` - Get outfits by category (t-shirts, trousers, etc.)
- `GET /api/outfit/season/{season}/category/{category}` - Personalized recommendations
- `POST /api/outfit/like` - Like an outfit item
- `GET /api/outfit/popularity/{item_id}` - Get item popularity score
- `POST /api/outfit/score` - Score outfit compatibility

### Virtual Try-On

- `POST /api/try-on/generate` - Generate try-on image (user + product)
- `POST /api/try-on/generate-full-outfit` - Generate full outfit try-on
- `POST /api/try-on/generate-full-outfit/on-sequential` - Sequential outfit generation (top → bottom → shoes)

### Body & Face Analysis

- `POST /api/shape/face` - Analyze face shape
- `POST /api/shape/body` - Analyze body shape

### Beauty Recommendations

- `POST /api/beauty/makeup` - Get makeup recommendations based on color season
- `POST /api/beauty/hair` - Get hair color recommendations

### User Profile

- `GET /api/user/profile` - Get user profile
- `POST /api/user/profile` - Create user profile
- `PUT /api/user/profile` - Update user profile
- `DELETE /api/user/profile` - Delete user profile
- `GET /api/user/profile/completeness` - Get profile completeness score

### User Color History

- `POST /api/user/color/save` - Save color analysis result
- `GET /api/user/color/results` - Get all color analysis history
- `GET /api/user/color/latest` - Get latest color analysis
- `DELETE /api/user/color/results/{result_id}` - Delete a result

### User Outfits

- `POST /api/user/outfits/like` - Like an outfit
- `DELETE /api/user/outfits/like/{item_id}` - Unlike an outfit
- `GET /api/user/outfits/liked` - Get all liked outfits
- `GET /api/user/outfits/liked/{item_id}` - Check if outfit is liked

---

## 🎯 Key Technical Strategies

### Ensemble Learning for Color Analysis

**Parallel Mode**: All 3 AI models (Gemini, GPT-4o, Claude) analyze simultaneously, then aggregate results using:

- **Voting**: Majority wins
- **Weighted Average**: Confidence-based (best accuracy)
- **Consensus**: Requires ≥67% agreement

**Hybrid Mode**: Two models analyze in parallel, third model acts as expert judge to evaluate and synthesize results for highest accuracy.

### Sequential Image Generation for Try-On

For full outfit visualization (top + bottom + shoes), we use sequential strategy:

1. Generate user wearing **upper garment** → save result
2. Use result as input + add **lower garment** → save result
3. Use result as input + add **shoes** → final image

This ensures proper layering and realistic outfit combinations.

---

## 🔬 Architecture

### Ensemble AI System

```
┌─────────────────────────────────────┐
│   User uploads selfie image         │
└──────────────┬──────────────────────┘
               │
    ┌──────────▼──────────┐
    │  Image Preprocessing│
    └──────────┬──────────┘
               │
   ┌───────────┼───────────┐
   │           │           │
┌──▼───┐  ┌───▼───┐  ┌───▼───┐
│Gemini│  │GPT-4o │  │Claude │
│ 2.5  │  │Vision │  │ 3.5   │
└──┬───┘  └───┬───┘  └───┬───┘
   │           │           │
   └───────────┼───────────┘
               │
    ┌──────────▼──────────┐
    │  Result Aggregation │
    │  • Voting            │
    │  • Weighted Average  │
    │  • Consensus         │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  Personalized Results│
    └─────────────────────┘
```

### Two Analysis Modes

**Parallel Ensemble** (Faster): All three models analyze simultaneously, results aggregated. Best for speed.

**Hybrid Ensemble** (More Accurate): Two models analyze, third acts as expert judge. Best for accuracy.

---

<div align="center">

**Built with ❤️ for Hack Seoul**

Made by Aki's Team

</div>
