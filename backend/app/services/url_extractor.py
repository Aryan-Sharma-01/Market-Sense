"""Service to extract content from URLs."""
from __future__ import annotations

import io
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

try:
    from io import BytesIO
except ImportError:
    BytesIO = io.BytesIO


def fetch_article_from_url(url: str) -> dict[str, Any]:
    """Fetch article content from a URL and extract text and images."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Try to find main article content
        article_text = ""
        article_title = ""
        
        # Try common article selectors
        article_selectors = [
            "article",
            ".article-content",
            ".article-body",
            ".story-content",
            ".post-content",
            "#article-body",
            ".content",
            "main article",
        ]
        
        article_element = None
        for selector in article_selectors:
            article_element = soup.select_one(selector)
            if article_element:
                break
        
        if article_element:
            article_text = article_element.get_text(separator=" ", strip=True)
        else:
            # Fallback: get all paragraph text
            paragraphs = soup.find_all("p")
            article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        
        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            article_title = title_tag.get_text(strip=True)
        else:
            h1_tag = soup.find("h1")
            if h1_tag:
                article_title = h1_tag.get_text(strip=True)
        
        # Extract main image if available
        article_image_bytes = None
        img_tags = soup.find_all("img")
        for img in img_tags:
            img_src = img.get("src") or img.get("data-src")
            if img_src:
                # Skip small icons/logos
                if any(skip in img_src.lower() for skip in ["logo", "icon", "avatar", "button"]):
                    continue
                
                try:
                    # Make absolute URL
                    if not img_src.startswith("http"):
                        img_src = urljoin(url, img_src)
                    
                    img_response = requests.get(img_src, headers=headers, timeout=5)
                    if img_response.status_code == 200:
                        article_image_bytes = img_response.content
                        # Validate it's actually an image
                        try:
                            Image.open(BytesIO(article_image_bytes))
                            break  # Found a valid image
                        except Exception:
                            article_image_bytes = None
                except Exception:
                    continue
        
        return {
            "title": article_title,
            "text": article_text,
            "image_bytes": article_image_bytes,
            "url": url,
        }
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing URL: {str(e)}")

