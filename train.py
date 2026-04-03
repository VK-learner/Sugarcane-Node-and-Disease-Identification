from ultralytics import YOLO

def main():
    # Use pretrained YOLOv8 medium weights
    model = YOLO("yolov8n.yaml")  # load a new model from YAML

    config_file_path = "E:/Vaibhav/data.yaml"  # your dataset config

    project = "E:/Vaibhav/yolov8-results"
    experiment = "My-Model-yolov8n"

    result = model.train(
        data=config_file_path,
        epochs=50,          # enough to converge
        batch=-1,            # RTX 3050 6GB VRAM optimal
        imgsz=640,           # preserve small fracture details
        device=0,
        patience=15,         # early stopping
        project=project,
        name=experiment,
        augment=True,        # strong data augmentation
        verbose=True,
        val=True,
        optimizer="auto",     # better for small datasets
        )

if __name__ == "__main__":
    main()