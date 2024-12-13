import re
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_yolo_output(line):
    """
    Parse YOLO training output dengan penanganan yang lebih robust.
    
    Args:
        line (str): Baris output dari proses training YOLO
    
    Returns:
        dict: Informasi parsing atau None jika tidak ada data yang ditemukan
    """
    # Debug: Log setiap baris yang masuk
    logger.debug(f"Processing line: {line}")

    # Regex patterns yang lebih fleksibel
    patterns = {
        'epoch_header': r'Epoch\s+GPU_mem\s+box_loss\s+cls_loss\s+dfl_loss\s+Instances\s+Size',
        'epoch_progress': r'(?P<current_epoch>\d+)/(?P<total_epochs>\d+)\s*(?P<gpu_mem>\d+\.\d+G)?\s*(?P<box_loss>\d+\.\d+)?\s*(?P<cls_loss>\d+\.\d+)?\s*(?P<dfl_loss>\d+\.\d+)?\s*(?P<instances>\d+)?\s*(?P<size>\d+)?.*?(?P<progress>\d+)%',
    }

    try:
        # Cek apakah ini header tabel Epoch
        if re.search(patterns['epoch_header'], line):
            logger.info("Header tabel Epoch ditemukan.")
            return {"status": "header_detected"}

        # Coba parsing progress epoch
        progress_match = re.search(patterns['epoch_progress'], line)
        if progress_match:
            # Ekstrak data dengan aman, menggunakan .get() untuk menghindari error
            data = progress_match.groupdict()
            
            # Konversi tipe data
            current_epoch = int(data['current_epoch']) if data['current_epoch'] else 0
            total_epochs = int(data['total_epochs']) if data['total_epochs'] else 100
            epoch_progress = int(data.get('progress') or 0)

            # Hitung progress keseluruhan
            total_progress = ((current_epoch - 1) / total_epochs * 100) + (epoch_progress / total_epochs)

            # Konstruksi response dengan konversi tipe yang aman
            return {
                "current_epoch": current_epoch,
                "total_epochs": total_epochs,
                "progress": round(min(total_progress, 100), 2),
                "epoch_progress": epoch_progress,
                "gpu_memory": data.get('gpu_mem'),
                "box_loss": float(data['box_loss']) if data.get('box_loss') else None,
                "cls_loss": float(data['cls_loss']) if data.get('cls_loss') else None,
                "dfl_loss": float(data['dfl_loss']) if data.get('dfl_loss') else None,
                "instances": int(data['instances']) if data.get('instances') else None,
                "size": int(data['size']) if data.get('size') else None,
                "show": True
            }

    except Exception as e:
        logger.error(f"Parsing error: {e}\n{traceback.format_exc()}")
        return None

    return None