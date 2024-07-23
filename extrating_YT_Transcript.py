import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def setup_driver(headless=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def click_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(2)  # Wait for scrolling to complete
        element.click()
        print(f"Successfully clicked element: {value}")
        return True
    except ElementClickInterceptedException:
        print(f"Element was intercepted: {value}. Attempting to click with JavaScript.")
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Could not click element: {value}. Error: {e}")
        return False

def get_transcript(url):
    driver = setup_driver(headless=False)
    driver.get(url)
    
    try:
        # Wait for the video to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "movie_player"))
        )
        print("Video player loaded successfully")
        
        # Click on the "...more" button
        more_button_xpath = "//tp-yt-paper-button[@id='expand']"
        if click_element(driver, By.XPATH, more_button_xpath):
            print("Successfully clicked '...more' button")
            time.sleep(5)
        else:
            print("Failed to click '...more' button")
        
        # Try to click on the "Show transcript" button
        show_transcript_xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-text-inline-expander/div[2]/ytd-structured-description-content-renderer/div/ytd-video-description-transcript-section-renderer/div[3]/div/ytd-button-renderer/yt-button-shape/button/div/span"
        
        if click_element(driver, By.XPATH, show_transcript_xpath):
            print("Successfully clicked 'Show transcript' button")
            time.sleep(5)  # Wait for transcript to load
            
            # Locate and extract transcript content
            transcript_container_xpath = "//ytd-transcript-renderer"
            transcript_segments_xpath = ".//ytd-transcript-segment-renderer"
            
            try:
                transcript_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, transcript_container_xpath))
                )
                transcript_segments = transcript_container.find_elements(By.XPATH, transcript_segments_xpath)
                
                print(f"Found {len(transcript_segments)} transcript segments")
                
                transcript = []
                for segment in transcript_segments:
                    timestamp = segment.find_element(By.CLASS_NAME, "segment-timestamp").text
                    text = segment.find_element(By.CLASS_NAME, "segment-text").text
                    transcript.append(f"{timestamp}: {text}")
                
                # Save transcript to a file in the script's directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                transcript_file = os.path.join(script_dir, "transcript.txt")
                with open(transcript_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(transcript))
                print(f"Transcript saved to: {transcript_file}")
                
                # Print first 5 lines of transcript
                print("\nFirst 5 lines of transcript:")
                for line in transcript[:5]:
                    print(line)
                
            except Exception as e:
                print(f"Error extracting transcript: {e}")
        else:
            print("Failed to click 'Show transcript' button")
        
        # Capture a screenshot for debugging
        screenshot_file = os.path.join(script_dir, "after_transcript_extraction.png")
        driver.save_screenshot(screenshot_file)
        print(f"Screenshot saved as: {screenshot_file}")
        
        print("Script completed. Transcript has been extracted if available.")
        
        # Keep the browser window open
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

def main():
    url = "https://www.youtube.com/watch?v=dNdbltSYaEM&t=4s"  # Replace with your YouTube video URL
    get_transcript(url)
    print("Script execution completed")

if __name__ == "__main__":
    main()