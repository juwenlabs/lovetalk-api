from pathlib import Path
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v38-critical-followups' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v38-critical-followups";', 'const SERVER_VERSION = "2026-08-23-potentia-v39-korean-selfharm-guard";', 1)
old='''(?:자해\\s*협박|자살|죽겠|죽어\\s*버리|죽어버리|죽을\\s*거|죽는다|극단적\\s*선택)'''
new='''(?:자해\\s*협박|자살|죽겠|죽어\\s*버(?:릴|리|린|려)|죽을\\s*거|죽는다|극단적\\s*선택)'''
assert old in s, 'starter self-harm pattern missing'
s=s.replace(old,new,1)
old2='''(?:헤어지|이별|떠나|그만)[^.\\n]{0,50}(?:죽어\\s*버리|죽어버리|죽겠|자살|죽을\\s*거)|(?:죽어\\s*버리|죽어버리|죽겠|자살|죽을\\s*거)[^.\\n]{0,70}(?:헤어지|이별|떠나|그만)'''
new2='''(?:헤어지|이별|떠나|그만)[^.\\n]{0,50}(?:죽어\\s*버(?:릴|리|린|려)|죽겠|자살|죽을\\s*거)|(?:죽어\\s*버(?:릴|리|린|려)|죽겠|자살|죽을\\s*거)[^.\\n]{0,70}(?:헤어지|이별|떠나|그만)'''
assert old2 in s, 'analysis self-harm pattern missing'
s=s.replace(old2,new2,1)
assert '2026-08-23-potentia-v39-korean-selfharm-guard' in s
p.write_text(s,encoding='utf-8')
print('v39 Korean self-harm guard patch applied')
