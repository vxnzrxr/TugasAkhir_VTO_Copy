import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

# 1. KONFIGURASI
model_name = "indobenchmark/indobert-base-p1" # Model dasar IndoBERT
output_dir = "./my_model"                     # Folder tempat menyimpan hasil training
num_labels = 4                                # Jumlah kategori (Kiri, Kanan, Keluar)

# 2. PERSIAPAN DATASET
class CommandDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def run_training():
    print("⏳ Membaca Dataset...")
    # Baca CSV
    df = pd.read_csv("dataset.csv")
    texts = df['text'].tolist()
    labels = df['label'].tolist()

    # Split Data (80% Training, 20% Testing untuk validasi akurasi)
    train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=0.2)

    print("⏳ Download Tokenizer & Model IndoBERT (Internet required)...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    # Tokenisasi Data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=32)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=32)

    # Bungkus jadi Dataset PyTorch
    train_dataset = CommandDataset(train_encodings, train_labels)
    val_dataset = CommandDataset(val_encodings, val_labels)

    # 3. SETUP TRAINING
    print("⏳ Memulai Training (Bisa 3-5 menit di CPU)...")
    training_args = TrainingArguments(
        output_dir='./results',          # Folder temporary
        num_train_epochs=5,              # Ulangi belajar 5 kali
        per_device_train_batch_size=4,   # Belajar 4 kalimat sekaligus
        logging_dir='./logs',
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )

    # 4. JALANKAN TRAINING
    trainer.train()

    # 5. SIMPAN MODEL HASIL TRAINING
    print(f"✅ Training Selesai! Menyimpan model ke {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("🎉 SIAP! Sekarang jalankan main.py")

if __name__ == "__main__":
    run_training()