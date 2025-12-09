#ifndef page_rsaencryption_h
#define page_rsaencryption_h

#include <QWidget>

QT_BEGIN_NAMESPACE
namespace Ui {
class page_rsaencryption;
}
QT_END_NAMESPACE

class page_rsaencryption : public QWidget
{
    Q_OBJECT

public:
    explicit page_rsaencryption(QWidget *parent = nullptr);
    ~page_rsaencryption();

private:
    Ui::page_rsaencryption *ui;
};

#endif // page_rsaencryption_h