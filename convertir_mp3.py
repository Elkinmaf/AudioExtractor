import os
import subprocess

def encontrar_ffmpeg():
    # Lugares comunes donde ffmpeg podría estar instalado
    posibles_rutas = [
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        "ffmpeg.exe"  # Si está en el PATH
    ]
    
    # Intentar encontrar ffmpeg
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
            
    # Si no se encuentra en las rutas predefinidas, buscar en el PATH
    try:
        resultado = subprocess.run(['where', 'ffmpeg'], 
                                 capture_output=True, 
                                 text=True)
        if resultado.returncode == 0:
            return resultado.stdout.strip().split('\n')[0]
    except:
        pass
        
    return None

def convertir_a_mp3():
    try:
        print("="*50)
        print("          Convertidor de MP4 a MP3")
        print("="*50)
        
        # Encontrar ffmpeg
        ffmpeg_path = encontrar_ffmpeg()
        if not ffmpeg_path:
            print("\n❌ Error: No se puede encontrar ffmpeg en el sistema")
            print("Por favor, verifica que ffmpeg está instalado correctamente")
            return
            
        print(f"\nffmpeg encontrado en: {ffmpeg_path}")
        
        # Solicitar archivo
        video_path = input("\nIngresa la ruta del archivo MP4 (o arrastra el archivo aquí): ").strip('"').strip("'")
        
        if not os.path.exists(video_path):
            print(f"\nError: No se encuentra el archivo: {video_path}")
            return
            
        audio_path = os.path.splitext(video_path)[0] + '.mp3'
        
        print("\nProcesando:")
        print(f"Entrada: {video_path}")
        print(f"Salida:  {audio_path}")
        
        comando = [
            ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-q:a', '2',
            audio_path
        ]
        
        print("\nConvirtiendo... Por favor espera.")
        
        resultado = subprocess.run(comando, 
                                 capture_output=True, 
                                 text=True)
        
        if resultado.returncode == 0:
            print("\n✅ ¡Conversión completada con éxito!")
            print(f"📝 El archivo se guardó en: {audio_path}")
        else:
            print("\n❌ Error en la conversión:")
            print(resultado.stderr)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Detalles del error:", e.__class__.__name__)
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    convertir_a_mp3()