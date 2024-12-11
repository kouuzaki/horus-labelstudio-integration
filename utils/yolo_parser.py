import traceback
import re


def parse_yolo_output(line):
    """
    Parse YOLO training output to extract current epoch and progress percentage.
    """
    print(f"Processing line: {line}")  # Debug log for the received line

    # Pola untuk mendeteksi header Epoch
    epoch_header_pattern = re.compile(r'Epoch\s+GPU_mem\s+box_loss\s+cls_loss\s+dfl_loss\s+Instances\s+Size')
    
    # Pola untuk progress dari epoch
    epoch_progress_pattern = re.compile(r'(\d+)/(\d+).*\s+(\d+)%\|')
    
    # Pola untuk mendeteksi GPU memory
    gpu_memory_pattern = re.compile(r'(\d+\.\d+G)')
    
    #Pola untuk mendeteksi Box Loss
    box_loss_pattern = re.compile(r'\s+(\d+\.\d+)\s+\d+\.\d+\s+\d+\.\d+')
    
    #Pola untuk mendeteksi Class Loss
    cls_loss_pattern = re.compile(r'\s+\d+\.\d+\s+(\d+\.\d+)\s+\d+\.\d+')
    
    #Pola untuk mendeteksi DFL Loss
    dfl_loss_pattern = re.compile(r'\s+\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)')
    
    #Pola untuk mendeteksi Instances
    instances_pattern = re.compile(r'(\d+)')
    
    #Pola untuk mendeteksi Size
    size_pattern = re.compile(r'(\d+)')

    try:
        # Periksa apakah baris ini adalah header tabel Epoch
        if epoch_header_pattern.search(line):
            print("Header tabel Epoch ditemukan.")
            return {"status": "header_detected"}
        
        # Cek progress epoch
        progress_match = epoch_progress_pattern.search(line)
        if progress_match:
            current_epoch = int(progress_match.group(1))
            total_epochs = int(progress_match.group(2))
            epoch_progress = int(progress_match.group(3))
            
            # Ekstrak informasi tambahan
            gpu_mem = gpu_memory_pattern.search(line)
            box_loss = box_loss_pattern.search(line)
            cls_loss = cls_loss_pattern.search(line)
            dfl_loss = dfl_loss_pattern.search(line)
            instances = instances_pattern.search(line)
            size = size_pattern.search(line)

            # Hitung kontribusi progress dari epoch saat ini
            total_progress = ((current_epoch - 1) / total_epochs * 100) + (epoch_progress / total_epochs)

            return {
            "current_epoch": current_epoch,
            "total_epochs": total_epochs,
            "progress": round(min(total_progress, 100), 2),
            "epoch_progress": epoch_progress,
            "gpu_memory": gpu_mem.group(1) if gpu_mem else None,
            "box_loss": float(box_loss.group(1)) if box_loss else None,
            "cls_loss": float(cls_loss.group(1)) if cls_loss else None,
            "dfl_loss": float(dfl_loss.group(1)) if dfl_loss else None,
            "instances": int(instances.group(1)) if instances else None,
            "size": int(size.group(1)) if size else None,
            "show": True 
            }
    
    except Exception as e:
        print(f"Parsing error: {e}\n{traceback.format_exc()}")

    return None
