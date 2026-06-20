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
            video_title = data.get('video_title', 'Cooking Video Stream')
            
            # 1. Fetch the secret API key from our active terminal memory space
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({"error": "Gemini API Key is missing from Render environment variables."}, status=500)
            
            # 2. Initialize the official Google GenAI Client
            client = genai.Client(api_key=api_key)
            
            # 3. Craft a bulletproof prompt using the exact video title grabbed by the client side
            prompt_instructions = f"""
            You are an elite culinary assistant. You are given a specific cooking video's details.
            
            Video Context Details:
            Video Title: {video_title}
            Video URL Link: {video_url}
            
            YOUR MISSION:
            1. Identify the specific dish mentioned in the Video Title.
            2. Using your expert culinary knowledge base, generate a complete ingredient list required to cook this exact style of dish perfectly.
            3. Generate a highly detailed, clean, step-by-step cooking instruction sequence array matching how this dish is traditionally created, making it super simple for a home chef.
            
            CRITICAL DEPLOYMENT INSTRUCTIONS:
            - Do not return a generic fallback recipe like spaghetti or placeholder text. You must generate the exact recipe corresponding to the Video Title provided: "{video_title}".
            - Write all output text in very simple, easy-to-read instructions.
            - Translate all keys, titles, ingredients, and instruction steps entirely into the chosen language code: '{target_lang}'.
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