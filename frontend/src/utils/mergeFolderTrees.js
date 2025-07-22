// utils/mergeFolderTrees.js
export function mergeFolderTrees(existing = [], uploaded = []) {
  const map = new Map();

  const merge = (a = {}, b = {}) => {
    return {
      id: a.id || b.id,
      name: a.name || b.name,
      count: (a.count || 0) + (b.count || 0),
      isExpanded: a.isExpanded ?? b.isExpanded ?? true,
      children: mergeFolderTrees(a.children || [], b.children || [])
    };
  };

  existing.forEach(f => map.set(f.name, { ...f }));
  uploaded.forEach(f => {
    const existing = map.get(f.name);
    map.set(f.name, existing ? merge(existing, f) : { ...f });
  });

  return Array.from(map.values());
}
