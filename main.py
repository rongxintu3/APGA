import argparse
from utils.data_provider import *
from model.target_attack_with_data_guided import *




parser = argparse.ArgumentParser()
# description of data
parser.add_argument('--dataset_name', dest='dataset', default='MS-COCO', choices=['CIFAR-10', 'ImageNet', 'FLICKR-25K', 'NUS-WIDE', 'MS-COCO'], help='name of the dataset')
parser.add_argument('--data_dir', dest='data_dir', default='/home/trc/datasets/dataset_mat/coco.h5', help='path of the dataset')
parser.add_argument('--image_size', dest='image_size', type=int, default=224, help='the width or height of images')
parser.add_argument('--number_channel', dest='channel', type=int, default=3, help='number of input image channels')
parser.add_argument('--database_file', dest='database_file', default='database_img.txt', help='the image list of database images')
parser.add_argument('--train_file', dest='train_file', default='train_img.txt', help='the image list of training images')
parser.add_argument('--test_file', dest='test_file', default='test_img.txt', help='the image list of test images')
parser.add_argument('--database_label', dest='database_label', default='database_label.txt', help='the label list of database images')
parser.add_argument('--train_label', dest='train_label', default='train_label.txt', help='the label list of training images')
parser.add_argument('--test_label', dest='test_label', default='test_label.txt', help='the label list of test images')
# model
parser.add_argument('--hash_method', dest='hash_method', default='CSQ', choices=['DPH', 'DPSH', 'HashNet', 'CSQ'], help='deep hashing methods')
parser.add_argument('--t_hash_method', dest='t_hash_method', default='CSQ', choices=['DPH', 'DPSH', 'HashNet', 'CSQ'], help='deep hashing methods')
parser.add_argument('--backbone', dest='backbone', default='VGG16', choices=['AlexNet', 'VGG11', 'VGG16', 'VGG19', 'ResNet18', 'ResNet50'], help='backbone network')
parser.add_argument('--code_length', dest='bit', type=int, default=32, help='length of the hashing code')
# training or test
parser.add_argument('--train', dest='train', type=bool, default=True, choices=[True, False], help='to train or not')
parser.add_argument('--test', dest='test', type=bool, default=True, choices=[True, False], help='to test or not')
parser.add_argument('--transfer', dest='transfer', type=bool, default=False, choices=[True, False], help='to test transferbility or not')
parser.add_argument('--t_backbone', dest='t_backbone', default='VGG16', help='targeted model')
parser.add_argument('--t_bit', dest='t_bit', type=int, default=32, help='target bit')
parser.add_argument('--batch_size', dest='batch_size', type=int, default=32, help='number of images in one batch')
parser.add_argument('--checkpoint_dir', dest='save', default='checkpoint/', help='models are saved here')
parser.add_argument('--test_dir', dest='test_dir', default='test/', help='output directory of test')
parser.add_argument('--n_epochs', dest='n_epochs', type=int, default=50, help='number of epoch')
parser.add_argument('--epoch_count', type=int, default=1, help='the starting epoch count, we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>, ...')
parser.add_argument('--n_epochs_decay', type=int, default=50, help='number of epochs to linearly decay learning rate to zero')
parser.add_argument('--learning_rate', dest='lr', type=float, default=1e-4, help='initial learning rate for adam')
parser.add_argument('--margin', dest='margin', type=float, default=0., help='x')
parser.add_argument('--percent', dest='percent', type=float, default=1.0, help='percent')
parser.add_argument('--gamma_softmax', dest='gamma_softmax', type=float, default=0.2, help='gamma_softmax')
parser.add_argument('--round', type=int, default=1, help='round')
parser.add_argument('--lr_policy', type=str, default='linear', help='learning rate policy. [linear | step | plateau | cosine]')
parser.add_argument('--lr_decay_iters', type=int, default=50, help='multiply by a gamma every lr_decay_iters iterations')
parser.add_argument('--print_freq', dest='print_freq', type=int, default=30, help='print the debug information every print_freq iterations')
parser.add_argument('--gpuid', dest='gpuid', type=int, default=0, help='GPU ID')
parser.add_argument('--rec_w', dest='rec_w', type=int, default=70, help='rec loss weight')
parser.add_argument('--load_model', dest='load', type=bool, default=False, help='if continue training, load the latest model: 1: true, 0: false')
args = parser.parse_args()

os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpuid)

dset_database = HashingDataset(args.data_dir, 'dataset')
dset_train = HashingDataset(args.data_dir, 'train')
dset_test = HashingDataset(args.data_dir, 'test')
num_database, num_test, num_train = len(dset_database), len(dset_test), len(dset_train)

database_loader = DataLoader(dset_database, batch_size=10, shuffle=False, num_workers=2)
train_loader = DataLoader(dset_train, batch_size=args.batch_size, shuffle=True, num_workers=2)
test_loader = DataLoader(dset_test, batch_size=10, shuffle=False, num_workers=2)

database_labels = dset_database.label
train_labels = dset_train.label
test_labels = dset_test.label

target_labels = database_labels.unique(dim=0)

model = TargetAttackGAN(args=args)
if args.train:
    if args.load:
        model.load_model()
    model.train(train_loader, target_labels, train_labels, database_loader, database_labels, num_database, num_train, num_test, test_loader, test_labels)


if args.test:
    model.load_model()
    model.test(target_labels, database_loader, test_loader, database_labels, test_labels, num_database, num_test)

if args.transfer:
    model.load_model()
    model.transfer_test(target_labels, database_loader, test_loader, database_labels, test_labels, num_database, num_test, args)
