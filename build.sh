pyinstaller --onefile --windowed batch_vmt.py
cp README.md LICENSE.txt base.vmt displacement_base.vmt dist/
cd dist/
rm -f batch_vmt_64bit_windows_exe.zip
zip batch_vmt_64bit_windows_exe *
