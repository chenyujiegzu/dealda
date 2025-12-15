#!/bin/bash

#@Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2025/12/15

DATA_DIR="/home/data4/PT2025_0005/NGC4147/"
DATE_LIST=("20250814")
OUT_CMD="commands.txt"

> "$OUT_CMD"

echo "Generating commands into $OUT_CMD ..."

for DATE in "${DATE_LIST[@]}"; do

    # mkdir datedir
    mkdir -p "${DATE}"
    chmod 777 "${DATE}"

    # ================================
    # transientx_fil commands
    # ================================
    echo "" >> "$OUT_CMD"

    echo "transientx_fil -v -o ${DATE}/${DATE}_NGC4147 -t 4 --zapthre 3.0 --dms 10 --ddm 0.1 --ndm 500 --thre 7 --minw 0.0005 --maxw 0.5 -l 0.5 --drop -z kadaneF 8 4 zdot --psrfits $DATA_DIR/$DATE/*.fits" >> "$OUT_CMD"


    # ================================
    # replot_fil commands
    # ================================
    echo "" >> "$OUT_CMD"

    echo "replot_fil -v -t 4 --zapthre 3.0 --srcname NGC4147 --ra 12:10:06.15 --dec +18:32:31.8 --telescope FAST --dmcutoff 0.01 --widthcutoff 0.01 --snrcutoff 7 --snrloss 0.1 --zap --zdot --kadane 8 4 7 --candfile ${DATE}/${DATE}*.cands --clean --psrfits $DATA_DIR/$DATE/*.fits" >> "$OUT_CMD"

    echo "" >> "$OUT_CMD"
done

echo "Done! All commands have been written to $OUT_CMD"

chmod 777 "$OUT_CMD"


# ============================================
# create run_commands.sh
# ============================================
cat > run_commands.sh << 'EOF'
#!/bin/bash

CMD_FILE="commands.txt"

echo "==============================="
echo " Running transientx_fil jobs..."
echo "==============================="

grep "^transientx_fil" "$CMD_FILE" | parallel -j 4

echo "All transientx_fil jobs completed!"
echo

wait

echo "==============================="
echo " Running replot_fil jobs..."
echo "==============================="

grep "^replot_fil" "$CMD_FILE" | parallel -j 4

echo "All replot_fil jobs completed!"
echo "==============================="
echo " All processing done!"
echo "==============================="
EOF

chmod 777 run_commands.sh
