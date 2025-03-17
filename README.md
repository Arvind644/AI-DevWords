# Technical Blog Generator

An AI-powered technical blog generator that creates high-quality technical content using Exa AI. This application helps generate technical blog posts, tutorials, and comprehensive guides based on recent technology trends and developments.

## Features

- Generate technical blog posts from recent developments
- Create code examples and tutorials
- Track technology trends and updates
- Generate comprehensive technical guides
- AI-powered content generation
- Modern Streamlit web interface

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   EXA_API_KEY=your_exa_api_key
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `utils/`: Utility functions and helpers
  - `blog_generator.py`: Blog generation logic
  - `tech_tracker.py`: Technology trend tracking
  - `content_processor.py`: Content processing utilities

## Usage

1. Select the type of content you want to generate
2. Input relevant keywords or topics
3. Configure generation parameters
4. Generate and preview the content
5. Export or publish the generated content

## License

MIT License 