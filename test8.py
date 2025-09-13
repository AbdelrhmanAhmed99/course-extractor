import os
import time
import json
import threading
from typing import List, Optional, Generator, Tuple
from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from firecrawl.firecrawl import FirecrawlApp as FirecrawlClient
except ImportError:
    from firecrawl import Firecrawl as FirecrawlClient


class CourseSchema(BaseModel):
    course_name: str = Field(..., description="Title of the course / programme")
    level: Optional[str] = Field(None, description="Undergraduate, Postgraduate, Diploma, etc.")
    fees: Optional[str] = Field(None, description="Fees or cost info")
    intake_date: Optional[str] = Field(None, description="Next intake or start date")
    requirements: Optional[str] = Field(None, description="Entry requirements or prerequisites")
    description: Optional[str] = Field(None, description="Course description / overview")
    duration: Optional[str] = Field(None, description="Course duration")
    source_url: Optional[str] = Field(None, description="URL of the course page")


def extract_course_details(fc: FirecrawlClient, course_urls: List[str]) -> Generator[Tuple[str, dict], None, None]:
    """
    Generator that yields progress logs and course data one at a time.
    Yields:
        (log_message, None) -> for status updates
        (None, course_dict) -> for extracted courses
    """
    for i, url in enumerate(course_urls, 1):
        yield f"[{i}/{len(course_urls)}] Extracting from {url}", None
        try:
            print(f"Starting extraction for: {url}")
            
            # Add timeout to prevent hanging (Windows compatible)
            result = None
            error_occurred = None
            
            def extract_worker():
                nonlocal result, error_occurred
                try:
                    result = fc.extract(
                        urls=[url],
                        prompt=(
                            "Extract full details of this course: course name, level, fees (UK and International if available),"
                            "intake / year of entry, entry requirements, full description, duration."
                            "Return a structured object with these fields."
                        ),
                        schema={
                            "type": "object",
                            "properties": {
                                "course_name": {"type": "string"},
                                "level": {"type": "string"},
                                "fees": {"type": "string"},
                                "intake_date": {"type": "string"},
                                "requirements": {"type": "string"},
                                "description": {"type": "string"},
                                "duration": {"type": "string"}
                            },
                            "required": ["course_name"]
                        },
                        enable_web_search=False
                    )
                except Exception as e:
                    error_occurred = e
            
            # Start extraction in a thread
            thread = threading.Thread(target=extract_worker)
            thread.daemon = True
            thread.start()
            
            # Wait for 60 seconds max
            thread.join(timeout=60)
            
            if thread.is_alive():
                print(f"Extraction timed out for: {url}")
                yield f"⏰ Timeout extracting {url} (60s limit)", None
                continue
            
            if error_occurred:
                print(f"Error extracting {url}: {error_occurred}")
                yield f"❌ Error extracting {url}: {error_occurred}", None
                continue
                
            if not result:
                print(f"No result for: {url}")
                yield f"⚠️ No result for {url}", None
                continue
                
            print(f"Extraction completed for: {url}")
                
        except Exception as e:
            print(f"Error extracting {url}: {e}")
            yield f"❌ Error extracting {url}: {e}", None
            continue

        if not result or result.data is None:
            yield f"⚠️ No data for {url}", None
            continue

        raw = result.data
        items = raw if isinstance(raw, list) else [raw]
        for d in items:
            if isinstance(d, dict):
                d["source_url"] = url
                yield None, d
        time.sleep(3)  # 3 second gap between requests


def extract_all_courses(course_urls: List[str]) -> list:
    """
    Extracts all courses and returns a list of unique courses.
    """
    load_dotenv()
    API_KEY = os.getenv("FIRECRAWL_API_KEY")
    if not API_KEY:
        raise EnvironmentError("FIRECRAWL_API_KEY not set in .env file")

    fc = FirecrawlClient(api_key=API_KEY)

    results = []
    seen = set()
    for log, course in extract_course_details(fc, course_urls):
        if course:
            key = course.get("course_name", "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                results.append(course)

    with open("courses_full.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


if __name__ == "__main__":
    # Test with just the problematic URL
    course_urls = [
        "https://www.liverpool.ac.uk/courses/accounting-and-finance-bsc-hons",
        "https://www.leedsbeckett.ac.uk/courses/applied-sports-studies-tennis-bsc",
        "https://www.leedsbeckett.ac.uk/courses/accounting-finance-ba",
        "https://www.leedsbeckett.ac.uk/courses/criminology-psychology-ba",
        "https://www.liverpool.ac.uk/courses/aerospace-engineering-beng-hons",
        "https://www.liverpool.ac.uk/courses/aerospace-engineering-with-pilot-studies-meng",
        "https://www.brighton.ac.uk/courses/study/secondary-biology-pgce.aspx",
        "https://www.brighton.ac.uk/courses/study/secondary-english-pgce.aspx",
        "https://www.brighton.ac.uk/courses/study/secondary-physics-with-mathematics-pgce.aspx",
        "https://www.brighton.ac.uk/courses/study/accounting-acca-msc-pgcert-pgdip.aspx",
        "https://www.hw.ac.uk/study/postgraduate/actuarial-management-with-data-science",
        "https://search.hw.ac.uk/s/redirect?collection=heriot-watt~sp-programmes&url=https%3A%2F%2Fwww.hw.ac.uk%2Fstudy%2Fpostgraduate%2Factuarial-science&auth=Xd4u87QuXoiMqEF5DLMWIg&profile=programmes&rank=3&query=%21FunDoesNotExist%3Apadrenull+%7Clevel%3A%22%24%2B%2B+Postgraduate+%24%2B%2B%22",
        "https://www.hw.ac.uk/study/postgraduate/actuarial-science-management",
        "https://search.hw.ac.uk/s/search.html?collection=heriot-watt%7Esp-programmes&profile=programmes&f.Level%7Clevel=Postgraduate&gscope1=uk&query=",
        "https://www.cesarritzcolleges.edu/en/program/bachelor-of-science-in-hospitality-business-management/"
    ]
    extract_all_courses(course_urls)
