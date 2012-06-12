from xdg import RecentFiles

rf = RecentFiles.RecentFiles()
rf.parse()
print(rf.getFiles()[0])
