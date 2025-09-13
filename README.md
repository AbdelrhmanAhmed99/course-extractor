# Course Extractor

A powerful web application that extracts detailed course information from university websites using Firecrawl API and displays results in real-time.

## Features

- 🔍 **Real-time Course Extraction** - Extract course details from multiple university URLs simultaneously
- 📊 **Live Progress Tracking** - See extraction progress and results as they happen
- 🎯 **Comprehensive Data** - Extract course name, level, fees, requirements, duration, and more
- 💾 **JSON Export** - Download individual courses or entire batch as JSON
- 🚀 **Streamlit Interface** - Beautiful, responsive web interface
- ⏱️ **Timeout Protection** - 60-second timeout per URL to prevent hanging
- 🔄 **Rate Limiting** - 3-second gaps between requests for API stability

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd course-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Firecrawl API key:
   - Get your API key from [Firecrawl](https://firecrawl.dev)
   - Edit the `.env` file and add: `FIRECRAWL_API_KEY=your_api_key_here`

## Usage

### Streamlit Web App (Recommended)
```bash
streamlit run streamlit_app.py
```

### Command Line
```bash
python test8.py
```

## How to Use

1. **Enter Course URLs** - Add university course page URLs (one per line)
2. **Click Extract** - Start the extraction process
3. **Watch Live Results** - See courses appear in real-time as they're processed
4. **Download Results** - Export individual courses or the entire batch as JSON

## Supported Universities

The extractor works with most university course pages, including:
- University of Liverpool
- Leeds Beckett University
- University of Brighton
- Heriot-Watt University
- And many more...

## API Requirements

- **Firecrawl API Key** - Required for web scraping functionality
- **Internet Connection** - For accessing university websites

## Technical Details

- **Backend**: Python with Firecrawl API
- **Frontend**: Streamlit
- **Data Format**: JSON
- **Timeout**: 60 seconds per URL
- **Rate Limiting**: 3 seconds between requests

## Troubleshooting

- **Timeout Issues**: Some URLs may timeout after 60 seconds - this is normal for complex pages
- **API Errors**: Check your Firecrawl API key and quota
- **No Results**: Ensure URLs are direct course pages, not search results

## License

MIT License - feel free to use and modify as needed.
