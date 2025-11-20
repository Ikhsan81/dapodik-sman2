import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dapodik SMAN 2 P.Siantar", layout="wide")

# --- CLASS UNTUK PDF ---
class PDF(FPDF):
    def header(self):
        # Logo (Opsional, jika ada file logo.png)
        # self.image('logo.png', 10, 8, 33)
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PEMERINTAH PROVINSI SUMATERA UTARA', 0, 1, 'C')
        self.cell(0, 5, 'DINAS PENDIDIKAN', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 5, 'SMA NEGERI 2 PEMATANGSIANTAR', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Jl. Patuan Anggi No. 8, Pematangsiantar, Kode Pos: 21146', 0, 1, 'C')
        self.cell(0, 5, 'E-mail: smandups@yahoo.co.id', 0, 1, 'C')
        self.ln(5)
        self.line(10, 35, 285, 35) # Garis Horizontal
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}/{{nb}} - Dicetak pada: {datetime.now().strftime("%d-%m-%Y")}', 0, 0, 'C')

# --- FUNGSI UTAMA ---
def main():
    st.title("🏫 Aplikasi Verifikasi Dapodik - SMAN 2 Pematangsiantar")
    
    # Sidebar Menu
    menu = ["Dashboard", "Input Data", "Upload File", "Cetak PDF"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Inisialisasi Data di Session State (Agar data tidak hilang saat refresh)
    if 'data_siswa' not in st.session_state:
        # Struktur data awal (kosong)
        st.session_state['data_siswa'] = pd.DataFrame(columns=[
            "NISN", "Nama Lengkap", "Kelas", "JK", "Tempat Lahir", 
            "Tanggal Lahir", "Nama Orangtua", "Alamat", "Agama"
        ])

    # --- DASHBOARD (Lihat Data) ---
    if choice == "Dashboard":
        st.subheader("Data Siswa Terdaftar")
        
        df = st.session_state['data_siswa']
        
        # Filter Kelas
        if not df.empty:
            kelas_list = ["Semua"] + list(df['Kelas'].unique())
            selected_kelas = st.selectbox("Filter Kelas:", kelas_list)
            
            if selected_kelas != "Semua":
                df = df[df['Kelas'] == selected_kelas]

            st.dataframe(df, use_container_width=True)
            st.info(f"Total Siswa: {len(df)} Orang")
            
            # Statistik Gender
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    jk_counts = df['JK'].value_counts()
                    st.bar_chart(jk_counts)
        else:
            st.warning("Belum ada data siswa. Silakan Input atau Upload file.")

    # --- INPUT DATA MANUAL ---
    elif choice == "Input Data":
        st.subheader("Input Data Siswa Baru")
        with st.form("form_siswa"):
            col1, col2 = st.columns(2)
            with col1:
                nisn = st.text_input("NISN")
                nama = st.text_input("Nama Lengkap")
                kelas = st.selectbox("Kelas", ["XII MIPA 1", "XII MIPA 2", "XII MIPA 3", "XII MIPA 4", "XII MIPA 5", "XII MIPA 6", "XII MIPA 7", "XII IPS 1", "XII IPS 2", "XII IPS 3"])
                jk = st.radio("Jenis Kelamin", ["L", "P"])
            with col2:
                tmp_lahir = st.text_input("Tempat Lahir")
                tgl_lahir = st.date_input("Tanggal Lahir", min_value=datetime(2000, 1, 1))
                ortu = st.text_input("Nama Orangtua")
                alamat = st.text_area("Alamat")
                agama = st.selectbox("Agama", ["Islam", "Kristen", "Katholik", "Hindu", "Buddha"])
            
            submit = st.form_submit_button("Simpan Data")
            
            if submit:
                new_data = {
                    "NISN": nisn, "Nama Lengkap": nama, "Kelas": kelas, "JK": jk,
                    "Tempat Lahir": tmp_lahir, "Tanggal Lahir": tgl_lahir.strftime("%d %B %Y"),
                    "Nama Orangtua": ortu, "Alamat": alamat, "Agama": agama
                }
                st.session_state['data_siswa'] = pd.concat([st.session_state['data_siswa'], pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"Siswa {nama} berhasil ditambahkan!")

    # --- UPLOAD FILE ---
    elif choice == "Upload File":
        st.subheader("Upload File CSV/Excel")
        st.write("Gunakan format tabel sederhana: NISN, Nama Lengkap, Kelas, JK, dll.")
        
        uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    # Mencoba membaca file CSV (termasuk file mentah Anda)
                    # Kita akan mencoba membersihkan data mentah secara otomatis
                    raw_df = pd.read_csv(uploaded_file, header=None)
                    
                    # Logika pembersihan sederhana untuk file CSV Anda yang berantakan
                    # Kita cari baris yang mengandung pola NISN atau Kelas
                    clean_data = []
                    for index, row in raw_df.iterrows():
                        row_str = row.astype(str).values
                        # Deteksi baris data (biasanya kolom ke-4 atau 5 adalah NISN)
                        if len(row) > 10 and row[5] in ['IPA', 'IPS']: # Deteksi kolom Jurusan
                            clean_data.append({
                                "NISN": row[3],
                                "Nama Lengkap": row[7],
                                "Kelas": row[6],
                                "JK": row[10],
                                "Tempat Lahir": row[8],
                                "Tanggal Lahir": row[9],
                                "Nama Orangtua": row[11],
                                "Alamat": row[12],
                                "Agama": row[15]
                            })
                    
                    if clean_data:
                        df_new = pd.DataFrame(clean_data)
                        st.session_state['data_siswa'] = pd.concat([st.session_state['data_siswa'], df_new], ignore_index=True)
                        st.success(f"Berhasil mengimpor {len(df_new)} data dari format khusus SMAN 2!")
                    else:
                        # Fallback jika format CSV biasa
                        df = pd.read_csv(uploaded_file)
                        st.session_state['data_siswa'] = pd.concat([st.session_state['data_siswa'], df], ignore_index=True)
                        st.success("Data berhasil diupload (Format Standar).")

                else:
                    df = pd.read_excel(uploaded_file)
                    st.session_state['data_siswa'] = pd.concat([st.session_state['data_siswa'], df], ignore_index=True)
                    st.success("Data Excel berhasil diupload.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

    # --- CETAK PDF ---
    elif choice == "Cetak PDF":
        st.subheader("Cetak Laporan PDF")
        
        df_print = st.session_state['data_siswa']
        
        if st.button("Generate PDF"):
            if df_print.empty:
                st.error("Tidak ada data untuk dicetak.")
            else:
                pdf = PDF('L', 'mm', 'A4') # Landscape
                pdf.alias_nb_pages()
                pdf.add_page()
                
                # Judul Laporan
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 10, 'DAFTAR VALIDASI DAN VERIFIKASI DAPODIK SISWA KELAS XII', 0, 1, 'C')
                pdf.ln(2)

                # Header Tabel
                pdf.set_font('Arial', 'B', 8)
                pdf.set_fill_color(200, 220, 255)
                
                # Definisi Lebar Kolom
                cols = [10, 25, 60, 25, 10, 30, 40, 50, 20]
                headers = ["No", "NISN", "Nama Lengkap", "Kelas", "L/P", "Tgl Lahir", "Orangtua", "Alamat", "Agama"]
                
                for i in range(len(headers)):
                    pdf.cell(cols[i], 8, headers[i], 1, 0, 'C', True)
                pdf.ln()

                # Isi Tabel
                pdf.set_font('Arial', '', 7)
                no = 1
                for index, row in df_print.iterrows():
                    # Cek jika halaman penuh
                    if pdf.get_y() > 180:
                        pdf.add_page()
                        # Print header lagi
                        pdf.set_font('Arial', 'B', 8)
                        for i in range(len(headers)):
                            pdf.cell(cols[i], 8, headers[i], 1, 0, 'C', True)
                        pdf.ln()
                        pdf.set_font('Arial', '', 7)

                    pdf.cell(cols[0], 6, str(no), 1, 0, 'C')
                    pdf.cell(cols[1], 6, str(row['NISN']), 1, 0, 'C')
                    pdf.cell(cols[2], 6, str(row['Nama Lengkap'])[:35], 1, 0, 'L') # Potong jika kepanjangan
                    pdf.cell(cols[3], 6, str(row['Kelas']), 1, 0, 'C')
                    pdf.cell(cols[4], 6, str(row['JK']), 1, 0, 'C')
                    pdf.cell(cols[5], 6, str(row['Tanggal Lahir']), 1, 0, 'L')
                    pdf.cell(cols[6], 6, str(row['Nama Orangtua'])[:20], 1, 0, 'L')
                    pdf.cell(cols[7], 6, str(row['Alamat'])[:30], 1, 0, 'L')
                    pdf.cell(cols[8], 6, str(row['Agama']), 1, 0, 'C')
                    pdf.ln()
                    no += 1

                # Tanda Tangan (Sesuai Dokumen)
                pdf.ln(10)
                y_sig = pdf.get_y()
                
                pdf.set_font('Arial', '', 8)
                pdf.cell(90, 5, "Diverifikasi Oleh Pengawas", 0, 0, 'C')
                pdf.cell(90, 5, "", 0, 0, 'C')
                pdf.cell(90, 5, "Pematangsiantar, Januari 2025", 0, 1, 'C')
                pdf.cell(90, 5, "", 0, 0, 'C')
                pdf.cell(90, 5, "", 0, 0, 'C')
                pdf.cell(90, 5, "Kepala SMA Negeri 2 Pematangsiantar", 0, 1, 'C')
                
                pdf.ln(20) # Ruang Tanda Tangan
                
                pdf.set_font('Arial', 'B', 8)
                pdf.cell(90, 5, "APUL SITUMORANG, S.Pd, M.M", 0, 0, 'C')
                pdf.cell(90, 5, "", 0, 0, 'C')
                pdf.cell(90, 5, "EDWAR SIMARMATA, S.Pd, M.Si", 0, 1, 'C')
                
                pdf.set_font('Arial', '', 8)
                pdf.cell(90, 5, "NIP: 196901261994121001", 0, 0, 'C')
                pdf.cell(90, 5, "", 0, 0, 'C')
                pdf.cell(90, 5, "NIP. 196605101988031006", 0, 1, 'C')

                # Output PDF ke String
                pdf_content = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_content).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Data_Siswa_SMAN2_PSiantar.pdf">👉 Klik di sini untuk Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    main()