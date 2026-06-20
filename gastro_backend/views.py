from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from google.genai import types

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
            
            # 2. Initialize the official Google GenAI Client
            client = genai.Client(api_key=api_key)
            
            # 3. Craft a bulletproof prompt instructing Gemini to analyze the YouTube URL content directly
            prompt_instructions = f"""
            You are a master culinary assistant trained to clean up chaotic video cooking instructions.
            Your task is to analyze the recipe shown in this video link: {video_url}
            
            MISSION:
            1. Extract or determine the primary title of the dish cooked in the video.
            2. Figure out the list of ingredients required.
            3. Break down the cooking process into a clean, simple, step-by-step array layout.
            
            CRITICAL DEPLOYMENT INSTRUCTIONS:
            - If you are unable to access the live video transcript directly, analyze the words inside the URL string itself to deduce what popular recipe it refers to, and generate a standard premium recipe for that dish instead of returning an error message.
            - Write all output text in very simple, easy-to-read instructions.
            - Translate all keys and strings entirely into the chosen language code: '{target_lang}'.
            - Return the response strictly as a valid JSON object matching this schema blueprint, without markdown code block formatting tags:
            {{
                "title": "Clean Dish Title",
                "ingredients": ["Ingredient item 1", "Ingredient item 2"],
                "steps": ["Step 1 description text", "Step 2 description text"]
            }}
            """
            
            # 4. Call gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_instructions,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            # 5. Parse the clean JSON text string back into a Python dictionary
            ai_data = json.loads(response.text)
            return JsonResponse(ai_data, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"AI Processing Error: {str(e)}"}, status=500)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)