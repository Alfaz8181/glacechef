from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from google.genai import types
import yt_dlp

# Standard homepage view
def home(request):
    return render(request, 'index.html')

# Core AI recipe distillation engine route listener
@csrf_exempt
def distill_recipe(request):
    if request.method == 'POST':
        try:
            # Parse incoming JSON payload parameters from JavaScript client
            data = json.loads(request.body)
            video_url = data.get('url')
            target_lang = data.get('lang', 'en')
            
            # 1. Fetch the secret API key from our active terminal memory space
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({"error": "Gemini API Key is missing from Render environment variables."}, status=500)
            
            video_context = 'Cooking Recipe Video Stream'
            description_context = ''
            
            # 2. Attempt to extract media metadata layer safely using yt-dlp
            try:
                ydl_opts = {
                    'skip_download': True,
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=False)
                    video_context = info_dict.get('title', video_context)
                    description_context = info_dict.get('description', '')
            except Exception as yt_err:
                # If Render's IP is geoblocked, log it and let Gemini handle it using the URL string directly!
                print(f"yt-dlp fallback triggered: {str(yt_err)}")
            
            # 3. Initialize the official Google GenAI Client
            client = genai.Client(api_key=api_key)
            
            # 4. Craft a strict prompt instructing Gemini to figure out the recipe even if metadata is light
            prompt_instructions = f"""
            You are a master culinary assistant trained to clean up short-form cooking instructions.
            Analyze the following video stream data context:
            URL: {video_url}
            Extracted Title: {video_context}
            Extracted Description: {description_context}
            
            Your mission:
            1. Identify what dish is being prepared based on the URL text, title, or description.
            2. Extract/generate an array list of all necessary ingredients.
            3. Extract/generate a clean, step-by-step array breakdown of the absolute simplest instructions to cook it.
            
            CRITICAL RULES:
            - Write the steps in incredibly simple, clear, easy-to-read language. Avoid fancy terms or jargon.
            - Translate all content entirely into the language matching the code: '{target_lang}'.
            - Return the final result strictly as a valid JSON object matching this schema blueprint, without markdown code block syntax:
            {{
                "title": "Clean Dish Title",
                "ingredients": ["Ingredient item 1", "Ingredient item 2"],
                "steps": ["Step 1 description text", "Step 2 description text"]
            }}
            """
            
            # 5. Fire off the structured text call directly to gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_instructions,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            # 6. Unpack response string text layers back into native Python dict memory values
            ai_data = json.loads(response.text)
            return JsonResponse(ai_data, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"AI Processing Error: {str(e)}"}, status=500)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)