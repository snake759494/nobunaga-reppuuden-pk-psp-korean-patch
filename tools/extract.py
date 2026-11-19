import pycdlib,os,sys
iso=pycdlib.PyCdlib();iso.open(sys.argv[1])
out=sys.argv[2]
for root,dirs,files in iso.walk(iso_path='/'):
    for f in files:
        p=root.rstrip('/')+'/'+f
        lp=os.path.join(out,p.lstrip('/').split(';')[0])
        os.makedirs(os.path.dirname(lp),exist_ok=True)
        iso.get_file_from_iso(lp,iso_path=p)
        rec=iso.get_record(iso_path=p)
        print(rec.extent_location(),rec.data_length,p)
