import json
import os
bugtype = ["fix npe NOT merge", "fix null pointer"]

def visityear(year):
    year=str(year)
    for root, dir, files in os.walk(year):
        html_urls = []

        for file in files:
            with open(root+"/"+file,"r",encoding="utf-8")as file_handle:
                f = json.load(file_handle)
                if int(f["total_count"]) == len(f["items"]):
                    # for item in f["items"]:
                    #     html_url = item["html_url"]
                    #     html_urls.append(html_url)
                        pass
                else:
                    print(f["total_count"], len(f["items"]))
                    reponame = file.split("$")[0].replace("#", "/")
                    bugtype_flag = int(file.split("$")[1][0:1])
                    bugtype_local = bugtype[bugtype_flag-1]
                    with open(year+"_incomplete","a",encoding="utf-8")as f_inc:
                        f_inc.write("%s         %s\n"%(reponame,bugtype_flag))

if __name__ == '__main__':
    os.chdir("fix_npe")
    print(os.getcwd())

    for i in range(2009,2019):
        if i==2012 or 1==2013:
            pass
        visityear(i)



