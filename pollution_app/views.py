from django.shortcuts import render
from .models import River, Prediction
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import tensorflow as tf
import joblib
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
import json
from datetime import date
from django.views.decorators.http import require_POST

# Завантаження моделі та scaler один раз
model_path = os.path.join(settings.BASE_DIR, 'pollution_app', 'predictor_model.h5')
scaler_path = os.path.join(settings.BASE_DIR, 'pollution_app', 'scaler.save')
model = tf.keras.models.load_model(model_path, compile=False)
scaler = joblib.load(scaler_path)

def index(request):
    prediction = None
    months = 1

    if request.method == 'POST':
        try:
            temperature = float(request.POST.get('temperature'))
            ph = float(request.POST.get('ph'))
            nitrogen = float(request.POST.get('nitrogen'))
            flow_speed = float(request.POST.get('flow_speed'))
            months = int(request.POST.get('months', 1))

            input_data = np.array([[temperature, ph, nitrogen, flow_speed]])
            input_scaled = scaler.transform(input_data)
            base_prediction = model.predict(input_scaled)[0][0]

            prediction = generate_series(base_prediction, months, nitrogen, flow_speed, temperature, ph)

        except Exception as e:
            prediction = f"Помилка: {str(e)}"

    return render(request, 'index.html', {'prediction': prediction, 'months': months})

def generate_series(base, months, nitrogen, flow_speed, temperature, ph):
    trend_coef = 1 + (0.1 * nitrogen) - (0.05 * flow_speed) + (0.03 * abs(ph - 7)) + (0.02 * (temperature - 10) / 10)
    trend = np.linspace(1.0, trend_coef, months)
    noise = np.random.normal(0, 0.015, months)
    result = base * trend + noise
    return [round(max(0, min(val, 1)), 3) for val in result]

def predict_for_river(request):
    river_id = request.GET.get('river_id')
    if not river_id:
        return JsonResponse({'error': 'Missing river_id'}, status=400)

    try:
        river = River.objects.get(pk=river_id)
        latest = Prediction.objects.filter(river=river).latest('created_at')

        input_data = np.array([[latest.temperature, latest.ph, latest.nitrogen, latest.flow_speed]])
        input_scaled = scaler.transform(input_data)
        base_prediction = model.predict(input_scaled)[0][0]

        forecast = generate_series(
            base_prediction, 6,
            latest.nitrogen,
            latest.flow_speed,
            latest.temperature,
            latest.ph
        )
        return JsonResponse({'river': river.name, 'forecast': forecast})

    except River.DoesNotExist:
        return JsonResponse({'error': 'River not found'}, status=404)
    except Prediction.DoesNotExist:
        return JsonResponse({'error': 'No prediction data found for this river'}, status=404)

def rivers_json(request):
    rivers = River.objects.all()
    data = [
        {
            'id': r.id,
            'name': r.name,
            'description': r.description,
            'lat': r.lat,
            'lon': r.lon
        }
        for r in rivers
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def create_prediction(request):
    try:
        body = json.loads(request.body)
        river_id = body.get('river_id')
        river = River.objects.get(pk=river_id)

        temperature = float(body.get('temperature'))
        ph = float(body.get('ph'))
        nitrogen = float(body.get('nitrogen'))
        flow_speed = float(body.get('flow_speed'))

        input_data = np.array([[temperature, ph, nitrogen, flow_speed]])
        input_scaled = scaler.transform(input_data)
        base_prediction = model.predict(input_scaled)[0][0]

        forecast = generate_series(base_prediction, 6, nitrogen, flow_speed, temperature, ph)

        Prediction.objects.create(
            river=river,
            date=date.today(),
            temperature=temperature,
            ph=ph,
            nitrogen=nitrogen,
            flow_speed=flow_speed,
            result=forecast
        )

        return JsonResponse({
            'status': 'ok',
            'river': river.name,
            'forecast': forecast
        })

    except River.DoesNotExist:
        return JsonResponse({'error': 'Річку не знайдено'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
