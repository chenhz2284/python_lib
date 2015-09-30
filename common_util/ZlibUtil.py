# encoding: utf8


import zlib


def compress(srcfile, destfile):
    compressor = zlib.compressobj()
    fin = open(srcfile, "rb")
    fout = open(destfile, "wb")
    while True:
        data = fin.read(1024)
        print("data", data)
        if data:
            fout.write(compressor.compress(data))
        else:
            break
    fout.write(compressor.flush())
    fin.close()
    fout.close()
    
def decompress(srcfile, destfile):
    decompressor = zlib.decompressobj()
    fin = open(srcfile, "rb")
    fout = open(destfile, "wb")
    while True:
        data = fin.read(1024)
        print("data", data)
        if data:
            fout.write(decompressor.decompress(data))
        else:
            break
    fout.write(decompressor.flush())
    fin.close()
    fout.close()
    
if __name__=="__main__":
    compress("a.txt", "a.txt.z")
#     decompress("a.txt.z", "b.txt")
    
    
    