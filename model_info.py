# --- Model Architecture Summary ---

def get_architecture_summary():
    """
    Returns a string representation of the DeepFake detection layers.
    """
    summary = """
    Model: "DeepFake_Scanner_v2"
    _________________________________________________________________
    Layer (type)                 Output Shape              Param #   
    =================================================================
    conv2d_1 (Conv2D)            (None, 222, 222, 32)      896       
    max_pooling2d_1 (MaxPooling) (None, 111, 111, 32)      0         
    conv2d_2 (Conv2D)            (None, 109, 109, 64)      18496     
    max_pooling2d_2 (MaxPooling) (None, 54, 54, 64)        0         
    flatten (Flatten)            (None, 186624)            0         
    dense_1 (Dense)              (None, 128)               23888000  
    dropout (Dropout)            (None, 128)               0         
    dense_2 (Dense)              (None, 1)                 129       
    =================================================================
    Total params: 23,907,521
    Trainable params: 23,907,521
    Non-trainable params: 0
    _________________________________________________________________
    """
    return summary

if __name__ == "__main__":
    print(get_architecture_summary())
