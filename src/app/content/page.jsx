import styles from "./content.module.css"

const Content = () => {

    const text = `a = 3
b = 100

[b > 10]
    {a > 1}
        out:
            b
    b = b - 10
`;

    return (
        <div className={styles.container}>
            <h3 className={styles.filename}>sample.clean</h3>
            <pre className={styles.code}>{text}</pre>
        </div>
    )
}

export default Content