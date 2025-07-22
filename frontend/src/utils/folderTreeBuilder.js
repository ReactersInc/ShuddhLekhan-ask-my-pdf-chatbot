export function buildFolderTreeFromFiles(files) {
  const root = [];

  files.forEach(file => {
    const parts = file.webkitRelativePath.split('/');
    const fileName = parts.pop();
    let currentLevel = root;

    parts.forEach((folderName, index) => {
      let existing = currentLevel.find(f => f.name === folderName);

      if (!existing) {
        existing = {
          id: parts.slice(0, index + 1).join('/'),
          name: folderName,
          count: 0,
          isExpanded: true,
          children: [],
          files: []
        };
        currentLevel.push(existing);
      }

      currentLevel = existing.children;
    });

    // At the final folder, store the file
    currentLevel.push({
      id: file.webkitRelativePath,
      name: fileName,
      type: 'file',
      file // optionally attach full File object
    });
  });

  return root;
}
