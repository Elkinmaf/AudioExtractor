import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor MP4 a MP3")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        
        # Paths
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.ffmpeg_path = None
        
        # Modo de selección (archivo o carpeta)
        self.input_mode = tk.StringVar(value="file")  # Por defecto modo archivo
        
        # Calidad
        self.quality = tk.StringVar(value="2")  # Valor predeterminado (0-9, donde 0 es la mejor calidad)
        
        # Interfaz de usuario
        self.create_widgets()
        
        # Buscar ffmpeg al iniciar
        self.ffmpeg_path = self.encontrar_ffmpeg()
        if self.ffmpeg_path:
            self.status_label.config(text=f"ffmpeg encontrado en: {self.ffmpeg_path}")
        else:
            self.status_label.config(text="⚠️ ffmpeg no encontrado. Por favor instálalo.")
            messagebox.warning("FFmpeg no encontrado", 
                             "No se encontró ffmpeg. Este programa es necesario para la conversión.")
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Convertidor de MP4 a MP3", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame de modo de entrada
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="Seleccionar:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Archivo específico", variable=self.input_mode, 
                       value="file", command=self.update_input_label).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Carpeta completa", variable=self.input_mode, 
                       value="folder", command=self.update_input_label).pack(side=tk.LEFT, padx=5)
        
        # Frame de entrada
        self.input_frame = ttk.LabelFrame(main_frame, text="Archivo de entrada")
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(self.input_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.browse_input_button = ttk.Button(self.input_frame, text="Examinar", command=self.browse_input)
        self.browse_input_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Frame de salida
        output_frame = ttk.LabelFrame(main_frame, text="Carpeta de salida")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Examinar", command=self.browse_output).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Frame de opciones
        options_frame = ttk.LabelFrame(main_frame, text="Opciones")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Calidad (0-9, 0=mejor):").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(options_frame, textvariable=self.quality, values=list(range(10)), width=5).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botón de conversión
        ttk.Button(main_frame, text="Convertir", command=self.start_conversion).pack(pady=10)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Estado
        self.status_label = ttk.Label(main_frame, text="Listo para convertir")
        self.status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Consola de salida
        console_frame = ttk.LabelFrame(main_frame, text="Registro")
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.console = tk.Text(console_frame, height=10, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para la consola
        scrollbar = ttk.Scrollbar(self.console, command=self.console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
    
    def update_input_label(self):
        if self.input_mode.get() == "file":
            self.input_frame.config(text="Archivo de entrada")
            self.input_path.set("")  # Limpiar entrada al cambiar de modo
        else:
            self.input_frame.config(text="Carpeta de entrada")
            self.input_path.set("")  # Limpiar entrada al cambiar de modo
    
    def browse_input(self):
        if self.input_mode.get() == "file":
            path = filedialog.askopenfilename(
                title="Seleccionar archivo MP4",
                filetypes=[("Archivos MP4", "*.mp4"), ("Todos los archivos", "*.*")]
            )
        else:
            path = filedialog.askdirectory(title="Seleccionar carpeta de entrada")
            
        if path:
            self.input_path.set(path)
            self.log_message(f"Entrada seleccionada: {path}")
    
    def browse_output(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if path:
            self.output_path.set(path)
            self.log_message(f"Carpeta de salida: {path}")
    
    def log_message(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)  # Desplazar al final
    
    def encontrar_ffmpeg(self):
        # Lugares comunes donde ffmpeg podría estar instalado
        posibles_rutas = [
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            "ffmpeg"  # Si está en el PATH en sistemas Unix/Linux
        ]
        
        # Intentar encontrar ffmpeg
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
                
        # Si no se encuentra en las rutas predefinidas, buscar en el PATH
        try:
            if os.name == 'nt':  # Windows
                resultado = subprocess.run(['where', 'ffmpeg'], 
                                        capture_output=True, 
                                        text=True)
            else:  # Unix/Linux/Mac
                resultado = subprocess.run(['which', 'ffmpeg'], 
                                        capture_output=True, 
                                        text=True)
                
            if resultado.returncode == 0:
                return resultado.stdout.strip().split('\n')[0]
        except Exception:
            pass
            
        return None
    
    def start_conversion(self):
        input_path = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_path or not output_dir:
            messagebox.showerror("Error", "Por favor selecciona la entrada y la carpeta de salida")
            return
            
        if not self.ffmpeg_path:
            messagebox.showerror("Error", "No se encontró ffmpeg. Por favor instálalo primero.")
            return
        
        # Lista de archivos a convertir
        mp4_files = []
        
        # Verificar el modo de entrada
        if self.input_mode.get() == "file":
            # Verificar si el archivo existe y es un MP4
            if not os.path.isfile(input_path):
                messagebox.showerror("Error", "El archivo seleccionado no existe")
                return
                
            if not input_path.lower().endswith('.mp4'):
                messagebox.showerror("Error", "El archivo seleccionado no es un MP4")
                return
                
            # Agregar el archivo a la lista
            mp4_files.append(os.path.basename(input_path))
            input_dir = os.path.dirname(input_path)
            
        else:  # Modo carpeta
            # Verificar si la carpeta existe
            if not os.path.isdir(input_path):
                messagebox.showerror("Error", "La carpeta seleccionada no existe")
                return
                
            # Obtener los archivos MP4 en la carpeta de entrada
            mp4_files = [f for f in os.listdir(input_path) if f.lower().endswith('.mp4')]
            input_dir = input_path
            
            if not mp4_files:
                messagebox.showinfo("Información", "No se encontraron archivos MP4 en la carpeta de entrada")
                return
        
        # Iniciar conversión en un hilo separado
        threading.Thread(
            target=self.convert_files, 
            args=(mp4_files, input_dir, output_dir)
        ).start()
    
    def convert_files(self, mp4_files, input_dir, output_dir):
        total_files = len(mp4_files)
        self.log_message(f"Iniciando conversión de {total_files} archivo(s)...")
        
        for idx, file in enumerate(mp4_files):
            try:
                # Actualizar interfaz
                progress = (idx / total_files) * 100
                self.progress_var.set(progress)
                self.status_label.config(text=f"Convirtiendo {idx+1}/{total_files}: {file}")
                self.root.update_idletasks()
                
                # Rutas de entrada y salida
                input_file = os.path.join(input_dir, file)
                output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '.mp3')
                
                self.log_message(f"Convirtiendo: {file}")
                
                # Comando de conversión
                comando = [
                    self.ffmpeg_path,
                    '-i', input_file,
                    '-vn',  # No video
                    '-acodec', 'libmp3lame',  # Codec MP3
                    '-q:a', self.quality.get(),  # Calidad
                    output_file
                ]
                
                # Ejecutar el comando
                proceso = subprocess.run(comando, 
                                      capture_output=True, 
                                      text=True)
                
                if proceso.returncode == 0:
                    self.log_message(f"✅ Convertido exitosamente: {file}")
                else:
                    self.log_message(f"❌ Error al convertir {file}:")
                    self.log_message(proceso.stderr)
                    
            except Exception as e:
                self.log_message(f"❌ Error al procesar {file}: {str(e)}")
        
        # Finalizar
        self.progress_var.set(100)
        self.status_label.config(text="Conversión completada")
        messagebox.showinfo("Completado", f"Se han procesado {total_files} archivo(s)")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP4toMP3Converter(root)
    root.mainloop()