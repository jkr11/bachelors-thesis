import numpy as np

def truncated_svd(matrix, k):
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    u_k = u[:, :k]
    s_k = s[:k]
    vh_k = vh[:k, :]
    return u_k @ np.diag(s_k) @ vh_k

def blocked_svd(blocked_tensor):
    u_dict, s_dict, vh_dict = {}, {}, {}
    
    for q, matrix in blocked_tensor.items():
        u, s, vh = np.linalg.svd(matrix, full_matrices=False)
        u_dict[q] = u
        s_dict[q] = s
        vh_dict[q] = vh
        
    return u_dict, s_dict, vh_dict

def blocked_svd_truncated(blocks, k:int):
    svds = {q: np.linalg.svd(b, full_matrices=False) for q, b in blocks.items()}
    
    all_s = np.concatenate([res[1] for res in svds.values()])
    all_s.sort()
    epsilon = all_s[::-1][min(k, len(all_s)) - 1]
    
    trunc_blocks = {}
    for q, (u, s, vh) in svds.items():
        mask = s >= epsilon
        trunc_blocks[q] = (u[:, mask], s[mask], vh[mask, :])
        
    return trunc_blocks